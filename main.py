import os
import pandas as pd

class ZFSPoolConfig:
    def __init__(self, name, drives_per_vdev, parity_per_vdev, total_vdevs, read_speed, write_speed, read_iops, write_iops):
        self.name = name
        self.drives_per_vdev = drives_per_vdev
        self.parity_per_vdev = parity_per_vdev
        self.total_vdevs = total_vdevs
        self.read_speed = read_speed
        self.write_speed = write_speed
        self.read_iops = read_iops
        self.write_iops = write_iops

    def calculate_performance(self):
        usable_drives = self.drives_per_vdev - self.parity_per_vdev

        # Adjust read and write speed calculations for RAIDZ
        total_read_speed = self.read_speed * self.drives_per_vdev * self.total_vdevs
        # For RAIDZ, write speed is approximately the speed of one drive per vdev
        total_write_speed = self.write_speed * self.total_vdevs

        # Adjust IOPS calculations for RAIDZ
        total_read_iops = self.read_iops * self.drives_per_vdev * self.total_vdevs
        # Write IOPS are significantly reduced due to parity overhead in RAIDZ
        total_write_iops = (self.write_iops * usable_drives * self.total_vdevs) / (self.parity_per_vdev + 1)

        # Resilver time estimate: less time is better for reliability
        # Wider vdevs increase resilver time, more vdevs decrease resilver time
        base_resilver_time = 100 * (self.drives_per_vdev / usable_drives) * (1 / self.total_vdevs)  # Base estimate for resilver time, lower is better

        # Resilvering performance estimates based on pool utilization
        resilver_25_full = base_resilver_time * 1.1  # Slight increase at 25% full
        resilver_50_full = base_resilver_time * 1.5  # Moderate increase at 50% full
        resilver_75_full = base_resilver_time * 2.0  # Significant increase at 75% full
        resilver_90_full = base_resilver_time * 3.0  # High increase at 90% full
        
        return {
            'Name': self.name,
            'Total Read Speed (MB/s)': total_read_speed,
            'Total Write Speed (MB/s)': total_write_speed,
            'Total Read IOPS': total_read_iops,
            'Total Write IOPS': total_write_iops,
            'Resilver Time 25% Full (lower is better)': resilver_25_full,
            'Resilver Time 50% Full (lower is better)': resilver_50_full,
            'Resilver Time 75% Full (lower is better)': resilver_75_full,
            'Resilver Time 90% Full (lower is better)': resilver_90_full
        }


def get_drive_specs():
    read_speed = int(input("Enter the read speed per drive (MB/s): "))
    write_speed = int(input("Enter the write speed per drive (MB/s): "))
    read_iops = int(input("Enter the read IOPS per drive: "))
    write_iops = int(input("Enter the write IOPS per drive: "))
    return read_speed, write_speed, read_iops, write_iops


def get_pool_configuration(read_speed, write_speed, read_iops, write_iops):
    name = input("Enter the pool configuration name: ")
    drives_per_vdev = int(input("Enter the number of drives per vdev: "))
    parity_per_vdev = int(input("Enter the number of parity drives per vdev: "))
    total_vdevs = int(input("Enter the total number of vdevs in the pool: "))

    return ZFSPoolConfig(name, drives_per_vdev, parity_per_vdev, total_vdevs, read_speed, write_speed, read_iops, write_iops)


def display_comparison(results):
    df = pd.DataFrame(results)
    print("\n================= ZFS Pool Configurations Comparison =================")
    print(df.to_string(index=False))
    print("======================================================================\n")


def main():
    os.system('clear' if os.name == 'posix' else 'cls')  # Clear the terminal for better readability
    read_speed, write_speed, read_iops, write_iops = get_drive_specs()
    
    pool_configs = []
    
    while True:
        pool = get_pool_configuration(read_speed, write_speed, read_iops, write_iops)
        pool_configs.append(pool)
        
        another = input("Would you like to add another pool configuration? (y/n): ").strip().lower()
        if another != 'y':
            break
    
    # Calculate performance for all pools
    results = [pool.calculate_performance() for pool in pool_configs]
    
    # Display comparison
    display_comparison(results)


if __name__ == "__main__":
    main()

