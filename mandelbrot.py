import numpy as np
import matplotlib.pyplot as plt

from power_pyro.monitor import Monitor

def mandelbrot(width=1000, height=700,
               xlim=(-2.5, 1.0), ylim=(-1.25, 1.25),
               max_iter=300):
    
    x = np.linspace(xlim[0], xlim[1], width, dtype=np.float64)
    y = np.linspace(ylim[0], ylim[1], height, dtype=np.float64)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y

    
    Z = np.zeros_like(C, dtype=np.complex128)
    it_count = np.zeros(C.shape, dtype=np.uint16)

    
    mask = np.ones(C.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask] * Z[mask] + C[mask]

        escaped = np.abs(Z) > 2.0

        newly_escaped = escaped & mask
        it_count[newly_escaped] = i

        mask &= ~escaped

        if not mask.any():
            break

    it_count[mask] = max_iter
    return it_count

if __name__ == "__main__":
    monitor = Monitor({'cpu': True, 'gpu': True, 'memory': True})

    monitor.start()
    iters = mandelbrot(
        width=1200,
        height=800,
        xlim=(-2.5, 1.0),
        ylim=(-1.25, 1.25),
        max_iter=10000
    )
    monitor.end()

    results = monitor.get_energy_consumed_by_components()

    print("Energia consumida: ")
    print(f"\t\tCPU: {results['cpu']:.5f} kWh\n\t\tGPU: {results['gpu']:.5f} kWh\n\t\tMemória: {results['memory']:.5f} kWh")

    plt.figure(figsize=(8, 6), dpi=150)
    
    plt.imshow(iters, extent=[-2.5, 1.0, -1.25, 1.25], origin="lower")
    plt.title("Conjunto de Mandelbrot")
    plt.xlabel("Re")
    plt.ylabel("Im")
    plt.tight_layout()
    plt.savefig("mandelbrot.png")
    plt.show()