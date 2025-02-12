import clr
import time
import os
import threading
from elevate import elevate
import subprocess
import psutil
import re

from ResourceUnavailableException import ResourceUnavailableException

if os.name == 'nt':
    elevate()

    #clr.AddReference(r"C:\Users\Alexa\OneDrive\Área de Trabalho\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

class Monitor:
    def __init__(self, cpu=True, gpu=True, memory=True):
        self.__sign = False
        self.__initial_time = 0.0
        self._cpu = cpu
        self._gpu = gpu
        self._memory = memory
        self._nvidia_gpu = False
        self._amd_gpu = False

        print(os.getpid())

        if os.name == 'nt':
            self.__thread = threading.Thread(target=self.windows_monitor)
            
            self.__computer = Computer()

            self.__computer.IsCpuEnabled = self._cpu 

            if gpu: 
                self.__computer.IsGpuEnabled = self._gpu
                
                if not self._is_there_dedicated_gpu():
                  raise ResourceUnavailableException("GPU", "Resource not found!")
                
            self.__computer.IsMemoryEnabled = self._memory 
        elif os.name == 'posix':
            self.__thread = threading.Thread(target=self.linux_monitor)
            
            if self._gpu:
                if self._is_there_nvidia_gpu():
                    self._nvidia_gpu = True
                elif self._is_there_amd_gpu():
                    self._amd_gpu = True
                else:
                    raise ResourceUnavailableException("GPU", "Resource not found!")
        else:
            raise ValueError("Unable to identify operating system")

        self.total_energy_cpu = 0.0
        self.total_energy_gpu = 0.0
        self.total_energy_memory = 0.0
        self.total_energy = 0.0
    
    def windows_monitor(self):
        self.__computer.Open()

        while not self.__sign:
            self.__initial_time = time.time() 

            time.sleep(10)
            
            period_time = time.time() 

            interval = period_time - self.__initial_time

            if self._cpu:     
                self.total_energy_cpu += (self.get_cpu_power() * self._get_cpu_percent_process() * interval)/3600000  # kWh
            if self._gpu:     
                self.total_energy_gpu += (self.get_gpu_power() * interval )/3600000  # kWh
            if self._memory:     
                self.total_energy_memory += (self.get_memory_power() * interval )/3600000 #kWh

            self.__initial_time = period_time
        
        self.__computer.Close()

    def linux_monitor(self):

        while not self.__sign:
            self.__initial_time = time.time() 

            time.sleep(10)
            
            period_time = time.time() 

            interval = period_time - self.__initial_time

            if self._cpu:     
                self.total_energy_cpu += (self.get_cpu_power()* interval)/3600000  # kWh
            if self._gpu:     
                self.total_energy_gpu += (self.get_gpu_power() * interval )/3600000  # kWh
            if self._memory:     
                self.total_energy_memory += (self.get_memory_power() * interval )/3600000 #kWh

            self.__initial_time = period_time
    
    def get_cpu_power(self):
        if os.name == 'nt':
            cpu = next((hardware for hardware in self.__computer.Hardware if hardware.HardwareType == HardwareType.Cpu), None)
            cpu.Update()
            time.sleep(0.1)

            power = next((sensor for sensor in cpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "CPU Package" or sensor.Name == "Package")))
            power = power.Value
        else:
            command = ["sudo", "perf", "stat", "-e", "power/energy-pkg/", "sleep", "0.1"]
            power = subprocess.run(command, capture_output=True, text=True)

            power = power.stderr.split(" ")
            power = [string for string in power if string.strip()]

            for index, string in enumerate(power):
                if string.find('\n\n') != -1:
                    power = power[index + 1]
                    power = power.replace(",", ".")
                    break
            
            power = float(power)/0.1
        
        return power
    
    def get_gpu_power(self):
        if os.name == 'nt':
            return self._get_generic_gpu_power_windows()
        else:
            if self._nvidia_gpu:
                return self._get_nvidia_gpu_power_linux()
            elif self._amd_gpu:
                return self._get_amd_gpu_power_linux()

    def _get_generic_gpu_power_windows(self):
        gpu = next((hardware for hardware in self.__computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                        hardware.HardwareType == HardwareType.GpuAmd or
                                                                        hardware.HardwareType == HardwareType.GpuNvidia)), None)
        gpu.Update()
        time.sleep(0.1)

        power = next((sensor for sensor in gpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "GPU Power" or sensor.Name == "GPU Package")))
        return power.Value
    
    def _get_nvidia_gpu_power_linux(self):
        if self._nvidia_gpu: 
            try:
                result = subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        check=True)
                
                return float(result.stdout.strip())
            except Exception as e:
                print('Error getting power from GPU: ', e.stderr.strip())
                return 0.0
            
    def _get_amd_gpu_power_linux(self):
        try:
            hwmon_path = '/sys/class/hwmon/'

            for hwmon in os.listdir(hwmon_path):
                hwmon_dir = os.path.join(hwmon_path, hwmon)
                
                name_file = os.path.join(hwmon_dir, 'name')
                if os.path.exists(name_file):
                    with open(name_file, 'r') as file:
                        device = file.read().strip()

                    if device == 'amdgpu':
                        power_file = os.path.join(hwmon_dir, 'power1_input')
                        if os.path.exists(power_file):
                            with open(power_file, 'r') as file:
                                power = float(file.read().strip())

                            power /= 10**6
                            return power
        except FileNotFoundError as e:
            print('Error getting power from GPU: ', e.stderr.strip())

    def get_memory_power(self):
        if os.name == 'nt':
            memory = next((hardware for hardware in self.__computer.Hardware if hardware.HardwareType == HardwareType.Memory), None)
            memory.Update()

            power = next((sensor for sensor in memory.Sensors if sensor.SensorType == SensorType.Data and sensor.Name == "Memory Used"))
            power = power.Value
            power *= 0.375
        else:
            pid = psutil.Process().pid
            process = psutil.Process(pid)

            power = process.memory_info().rss
            power /= (1024 ** 3)
            power *= 0.375
        
        return power
    
    def _is_there_dedicated_gpu(self):
        computer = Computer()
        computer.Open()
        computer.IsGpuEnabled = True

        gpu = next((hardware for hardware in computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                   hardware.HardwareType == HardwareType.GpuAmd or
                                                                   hardware.HardwareType == HardwareType.GpuNvidia)), None)
        
        if gpu != None:
            gpu.Update()
            time.sleep(0.1)

            if next((sensor for sensor in gpu.Sensors if sensor.Name == "D3D Dedicated Memory Used"), None) != None:
                computer.Close()
                return True
        
        computer.Close()
        return False
    
    def _is_there_nvidia_gpu(self):
        try:
            subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr= subprocess.PIPE, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
        
    def _is_there_amd_gpu(self):
        try:
            result = subprocess.check_output(['lspci', '-nnk'], universal_newlines=True)

            for line in result.splitlines():
                if re.search(r"( VGA | 3D )", line) and re.search(r"AMD", line.upper()): 
                    return True
            
            return False
        except Exception as e:
            raise Exception(f'Error checking for AMD graphics card:{e}')    

    def _get_cpu_percent_process(self):
        script_pid = os.getpid()
        sum_all = 0
        cpu_percent = 0
        for process in psutil.process_iter():
            try:
                with process.oneshot():
                    process_pid = process.pid
                    process_cpu_percent = process.cpu_percent()

                    if process_pid:
                        sum_all += process_cpu_percent

                        if process_pid == script_pid:
                            cpu_percent += process_cpu_percent
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
        if sum_all != 0:
            return cpu_percent/sum_all
        else:
            return 0.0
    
    def get_energy_consumed(self):
        if self._cpu:
            if self._gpu:
                if self._memory:
                    return {'cpu': self.total_energy_cpu, 'gpu': self.total_energy_gpu, 'memory': self.total_energy_memory}
                else:
                    return {'cpu': self.total_energy_cpu, 'gpu': self.total_energy_gpu}
            else:
                if self._memory:
                    return {'cpu': self.total_energy_cpu, 'memory': self.total_energy_memory}
                else:
                    return {'cpu': self.total_energy_cpu}
        else:
            return {}
        
    def get_total_energy_consumed(self):
        if self._cpu:
            self.total_energy += self.total_energy_cpu
        if self._gpu:
            self.total_energy += self.total_energy_gpu
        if self._memory:
            self.total_energy += self.total_energy_memory

        return self.total_energy
    
    def start(self):
        self.__thread.start()

    def end(self):
        self.__sign = True
        self.__thread.join()