import clr
import time
import threading

clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

class Monitor:
    def __init__(self, cpu=True, gpu=True, memory=True):
        self.sign = False
        self.initial_time = 0.0
        self.thread = threading.Thread(target=self.monitor)
        self.total_energy_cpu = 0.0
        self.total_energy_gpu = 0.0
        self.total_energy_memory = 0.0

        self.computer = Computer()

        self.computer.IsCpuEnabled = cpu  
        self.computer.IsGpuEnabled = gpu  
        self.computer.IsMemoryEnabled = memory 
    
    def monitor(self):
        self.computer.Open()

        while not self.sign:
            self.initial_time = time.time() 

            time.sleep(1)
            
            period_time = time.time() 

            interval = period_time - self.initial_time

            # Seria interval + 0.2s?
            if self.computer.IsCpuEnabled:     
                self.total_energy_cpu += (self.get_cpu_power().Value * (interval / 3600))/1000  # kWh
            if self.computer.IsGpuEnabled:     
                self.total_energy_gpu += (self.get_gpu_power().Value * (interval / 3600))/1000  # kWh
            if self.computer.IsMemoryEnabled:     
                self.total_energy_memory += (self.get_memory_power().Value * 0.375 * (interval / 3600))/1000 #kWh

            self.initial_time = period_time
        
        self.computer.Close()
    
    def get_cpu_power(self):
        cpu = next((hardware for hardware in self.computer.Hardware if hardware.HardwareType == HardwareType.Cpu), None)
        cpu.Update()
        time.sleep(0.1)
        
        return next((sensor for sensor in cpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "CPU Package" or sensor.Name == "Package")))
    
    def get_gpu_power(self):
        gpu = next((hardware for hardware in self.computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                        hardware.HardwareType == HardwareType.GpuAmd or
                                                        hardware.HardwareType == HardwareType.GpuNvidia)), None)
        gpu.Update()
        time.sleep(0.1)
        return next((sensor for sensor in gpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "GPU Power" or sensor.Name == "GPU Package")))
    
    def get_memory_power(self):
        memory = next((hardware for hardware in self.computer.Hardware if hardware.HardwareType == HardwareType.Memory), None)
        memory.Update()

        return next((sensor for sensor in memory.Sensors if sensor.SensorType == SensorType.Data and sensor.Name == "Memory Used"))
    
    def get_energy_consumed(self):
        if self.computer.IsCpuEnabled:
            if self.computer.IsGpuEnabled:
                if self.computer.IsMemoryEnabled:
                    return {'cpu': self.total_energy_cpu, 'gpu': self.total_energy_gpu, 'memory': self.total_energy_memory}
                else:
                    return {'cpu': self.total_energy_cpu, 'gpu': self.total_energy_gpu}
            else:
                return {'cpu': self.total_energy_cpu}
        else:
            return {}
    
    def start(self):
        self.thread.start()

    def end(self):
        self.sign = True
        self.thread.join()