import clr
import time
import os
import threading
from elevate import elevate
import subprocess
import psutil

from ResourceUnavailableException import ResourceUnavailableException

if os.name == 'nt':
    elevate()

    #clr.AddReference(r"C:\Users\Alexa\OneDrive\Área de Trabalho\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

class Monitor:
    def __init__(self, cpu=True, gpu=True, memory=True):
        self.sign = False
        self.initial_time = 0.0
        self.cpu = cpu
        self.gpu = gpu
        self.memory = memory

        if os.name == 'nt':
            self.thread = threading.Thread(target=self.windows_monitor)
            
            self.computer = Computer()

            self.computer.IsCpuEnabled = self.cpu 

            if gpu: 
                self.computer.IsGpuEnabled = self.gpu
                
                if not self.is_there_dedicated_gpu():
                  raise ResourceUnavailableException("GPU", "Resource not found!")
                
            self.computer.IsMemoryEnabled = self.memory 
        elif os.name == 'posix':
            self.thread = threading.Thread(target=self.linux_monitor)
            
            if self.is_there_nvidia_gpu():
                self.nvidia_gpu = True
        else:
            raise ValueError("Unable to identify operating system")

        self.total_energy_cpu = 0.0
        self.total_energy_gpu = 0.0
        self.total_energy_memory = 0.0
        self.total_energy = 0.0
    
    def windows_monitor(self):
        self.computer.Open()

        while not self.sign:
            self.initial_time = time.time() 

            time.sleep(10)
            
            period_time = time.time() 

            interval = period_time - self.initial_time

            if self.cpu:     
                self.total_energy_cpu += (self.get_cpu_power() * interval)/3600000  # kWh
            if self.gpu:     
                self.total_energy_gpu += (self.get_gpu_power() * interval )/3600000  # kWh
            if self.memory:     
                self.total_energy_memory += (self.get_memory_power() * interval )/3600000 #kWh

            self.initial_time = period_time
        
        self.computer.Close()

    def linux_monitor(self):

        while not self.sign:
            self.initial_time = time.time() 

            time.sleep(10)
            
            period_time = time.time() 

            interval = period_time - self.initial_time

            if self.cpu:     
                self.total_energy_cpu += (self.get_cpu_power()* interval)/3600000  # kWh
            if self.gpu:     
                self.total_energy_gpu += (self.get_gpu_power() * interval )/3600000  # kWh
            if self.memory:     
                self.total_energy_memory += (self.get_memory_power() * interval )/3600000 #kWh

            self.initial_time = period_time
    
    def get_cpu_power(self):
        if os.name == 'nt':
            cpu = next((hardware for hardware in self.computer.Hardware if hardware.HardwareType == HardwareType.Cpu), None)
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
            gpu = next((hardware for hardware in self.computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                            hardware.HardwareType == HardwareType.GpuAmd or
                                                                            hardware.HardwareType == HardwareType.GpuNvidia)), None)
            gpu.Update()
            time.sleep(0.1)

            power = next((sensor for sensor in gpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "GPU Power" or sensor.Name == "GPU Package")))
            power = power.Value
        else:
            if self.nvidia_gpu: 
                try:
                    result = subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True,
                                            check=True)
                    
                    power = float(result.stdout.strip())
                except Exception as e:
                    print('Error getting power from GPU: ', e.stderr.strip())
                    return 0.0

        return power
    
    def get_memory_power(self):
        if os.name == 'nt':
            memory = next((hardware for hardware in self.computer.Hardware if hardware.HardwareType == HardwareType.Memory), None)
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
    
    def check_cpu_type(self):
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('vendor_id'):
                        return line.strip().split(':')[1].strip()

        except FileNotFoundError:
            return None
    
    def is_there_dedicated_gpu(self):
        computer = Computer()
        computer.Open()
        computer.IsGpuEnabled = True

        gpu = next((hardware for hardware in computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                   hardware.HardwareType == HardwareType.GpuAmd)), None)
        
        if gpu != None:
            gpu.Update()
            time.sleep(0.1)

            if next((sensor for sensor in gpu.Sensors if sensor.Name == "D3D Shared Memory Total"), None) != None:
                computer.Close()
                return False
        
        computer.Close()
        return True
    
    def is_there_nvidia_gpu(self):
        try:
            subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr= subprocess.PIPE, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
    
    def get_energy_consumed(self):
        if self.cpu:
            if self.gpu:
                if self.memory:
                    return {'cpu': self.total_energy_cpu, 'gpu': self.total_energy_gpu, 'memory': self.total_energy_memory}
                else:
                    return {'cpu': self.total_energy_cpu, 'gpu': self.total_energy_gpu}
            else:
                if self.memory:
                    return {'cpu': self.total_energy_cpu, 'memory': self.total_energy_memory}
                else:
                    return {'cpu': self.total_energy_cpu}
        else:
            return {}
        
    def get_total_energy_consumed(self):
        if self.cpu:
            self.total_energy += self.total_energy_cpu
        if self.gpu:
            self.total_energy += self.total_energy_gpu
        if self.memory:
            self.total_energy += self.total_energy_memory

        return self.total_energy
    
    def start(self):
        self.thread.start()

    def end(self):
        self.sign = True
        self.thread.join()