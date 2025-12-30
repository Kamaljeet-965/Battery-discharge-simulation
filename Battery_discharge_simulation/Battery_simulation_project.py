"""
Battery Discharge Simulation
Author: Kamaljeet Sahoo
Description:
Physics-based simulation of battery SOC, terminal voltage,
and power delivery under load using first principles.
"""



"""
Battery Discharge Simulation Project
Physics Explanation:
- SOC (State of Charge): Percentage of remaining battery capacity (0-100%)
- Battery Capacity (Ah): Total charge battery can deliver in 1 hour
- Discharge Current (A): Rate at which battery is being discharged
- SOC(t) = SOC_initial - (∫I dt / Capacity) * 100
- Real batteries have internal resistance causing voltage drop: V = V_ocv - I*R_internal
- Peukert's Law: Effective capacity decreases at higher discharge rates
"""

import numpy as np
import matplotlib.pyplot as plt 
from scipy.integrate import cumulative_trapezoid
import warnings
warnings.filterwarnings('ignore')

"""
       Initializing battery parameters
        
        Physics Parameters:
        - capacity_Ah: Battery capacity in Ampere-hours (Ah)
        - initial_SOC: Starting State of Charge (0-100%)
        - nominal_voltage: Battery's nominal voltage (V)
        - internal_resistance: Causes voltage drop under load (Ohms)
        - peukert_exponent: Accounts for capacity loss at high rates (1.0-1.3)
 """

class Batterysimulator:
    def __init__(self, capacity_Ah=10, initial_soc=100, nominal_voltage=12):
        self.capacity_Ah = capacity_Ah
        self.initial_SOC = initial_soc  
        self.nominal_voltage = nominal_voltage
        self.internal_resistance = 0.05  
        self.peukert_exponent = 1.1  #ranges from 1.0 to 1.6 

        #coverting from Ah to As (ampere-second)
        self.capacity_As = capacity_Ah * 3600 
    """
        Applying Peukert's Law: Effective capacity decreases with higher discharge rates
        C_effective = C_nominal * (I_nom/I)^(k-1)
        where k is Peukert's exponent
        """
    
    def peukert_capacity(self, current):
        # Reference current 
        I_ref = self.capacity_Ah / 20  

        if current <= 0:
            return self.capacity_As
        
        #effective capacity factor 
        peukert_factor = (I_ref / current) ** (self.peukert_exponent - 1)
        
        peukert_factor = max(0.3, min(2.0, peukert_factor))  
        return self.capacity_As * peukert_factor

    def discharge_simulation(self, time_hours, current_profile='constant',
                           current_value=5, add_noise=True):
        
        """
        Simulation of battery discharge over time
        
        Physics:
        - SOC calculation: SOC(t) = SOC_initial - (∫I(t)dt / Capacity) * 100
        - Voltage calculation: V(t) = V_ocv(SOC) - I(t) * R_internal
        - V_ocv: Open Circuit Voltage, varies with SOC
        """

        time_seconds = time_hours * 3600 
        t = np.linspace(0, time_seconds, 1000)
        
        #current profile based on user selection
        if current_profile == 'constant':
            I = np.full_like(t, current_value)
        elif current_profile == 'pulsed':  
            I = current_value * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * t / 3600)))
        elif current_profile == 'ramp':
            I = current_value * (0.5 + 0.5 * t / time_seconds)
        elif current_profile == 'random':
            I = current_value * (0.7 + 0.6 * np.random.randn(len(t)))
            I = np.clip(I, 0.1 * current_value, 2 * current_value)
        else:
            raise ValueError("Invalid current profile.")
        
        #random noise to simulate real world condition 
        if add_noise:
            I += 0.05 * current_value * np.random.randn(len(t))

        #using cummulative trapezoidal integration
        Q_discharged = cumulative_trapezoid(I, t, initial=0)

        effective_capacities = np.array([self.peukert_capacity(i) for i in I])
        avg_effective_capacity = np.mean(effective_capacities)

        #SOC calculation
        SOC = self.initial_SOC - (Q_discharged / avg_effective_capacity) * 100
        SOC = np.clip(SOC, 0, 100)

        #calculating terminal volatage, remaning capacity and power output 
        OCV = self.nominal_voltage * (0.8 + 0.2 * SOC / 100)
        V_terminal = OCV - I * self.internal_resistance 

        remaining_capacity_Ah = self.capacity_Ah * SOC / 100

        power_W = V_terminal * I

        return {
            'time_hours': t / 3600, 
            'time_seconds': t,
            'current_A': I,
            'SOC_percent': SOC,  
            'voltage_V': V_terminal,
            'power_W': power_W,
            'remaining_capacity_Ah': remaining_capacity_Ah,
            'effective_capacity_As': avg_effective_capacity
        }
    
    """
        Creating comprehensive visualization of simulation results
        
        Physics Visualizations:
        1. SOC vs Time: Shows battery depletion
        2. Current Profile: Input to the system
        3. Voltage vs Time: Shows voltage sag under load
        4. Power vs Time: Energy delivery rate
        """

    def plot_results(self, results, save_plot=False):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Battery Discharge Simulation', 
                    fontsize=16, fontweight='bold')

        # Plot 1: SOC vs Time
        axes[0, 0].plot(results['time_hours'], results['SOC_percent'], 
                       'b-', linewidth=2, label='SOC')
        axes[0, 0].axhline(y=20, color='r', linestyle='--', 
                          alpha=0.5, label='20% Warning Level')
        axes[0, 0].axhline(y=0, color='r', linestyle='-', 
                          alpha=0.3, label='0% Cut-off')
        axes[0, 0].fill_between(results['time_hours'], 0, 
                               results['SOC_percent'], alpha=0.3, color='blue')
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('State of Charge (%)')
        axes[0, 0].set_title('Battery Discharge Curve')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()
        axes[0, 0].set_ylim(-5, 105)

        # Plot 2: Current Profile
        axes[0, 1].plot(results['time_hours'], results['current_A'], 
                       'g-', linewidth=2)
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Current (A)')
        axes[0, 1].set_title('Discharge Current Profile')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].fill_between(results['time_hours'], 0, 
                               results['current_A'], alpha=0.3, color='green')

        # Plot 3: Terminal Voltage
        axes[1, 0].plot(results['time_hours'], results['voltage_V'], 
                       'r-', linewidth=2)
        axes[1, 0].axhline(y=self.nominal_voltage * 0.9, color='orange', 
                          linestyle='--', alpha=0.7, label='Low Voltage Threshold')
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_ylabel('Voltage (V)')
        axes[1, 0].set_title('Terminal Voltage under Load')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()

        # Plot 4: Power Output
        axes[1, 1].plot(results['time_hours'], results['power_W'], 
                       'purple', linewidth=2)
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Power (W)')
        axes[1, 1].set_title('Power Delivery')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].fill_between(results['time_hours'], 0, 
                               results['power_W'], alpha=0.3, color='purple')

        plt.tight_layout()

        if save_plot:
            plt.savefig('battery_discharge.png', dpi=150, bbox_inches='tight')
            print("Plot saved as 'battery_discharge.png'")

        plt.show()

        self.print_summary(results)


    #printing summary of statistics 
    def print_summary(self, results):
        print("\n" + "=" * 60)
        print("BATTERY DISCHARGE SIMULATION")
        print("=" * 60)

        # calculating when SOC reach 0 
        zero_soc = np.where(results['SOC_percent'] <= 0)[0]
        if len(zero_soc) > 0:
            discharge_time = results['time_hours'][zero_soc[0]]
        else:
            discharge_time = results['time_hours'][-1]

        print(f"\nBattery Specifications:")
        print(f"  - Nominal Capacity: {self.capacity_Ah} Ah")
        print(f"  - Initial SOC: {self.initial_SOC}%")
        print(f"  - Nominal Voltage: {self.nominal_voltage} V")
       
        print(f"\nCurrent Profile Analysis:")
        print(f"  - Average Current: {np.mean(results['current_A']):.2f} A")
        print(f"  - Max Current: {np.max(results['current_A']):.2f} A")
        print(f"  - Min Current: {np.min(results['current_A']):.2f} A")
      
        print(f"\nDischarge Performance:")
        print(f"  - Time to full discharge: {discharge_time:.2f} hours")
        print(f"  - Average Voltage: {np.mean(results['voltage_V']):.2f} V")
        print(f"  - Energy Delivered: {np.trapz(results['power_W'], results['time_seconds'])/3600:.2f} Wh")
        
        print(f"\nPhysics Parameters Applied:")
        print(f"  - Internal Resistance: {self.internal_resistance} Ω")
        print(f"  - Peukert Exponent: {self.peukert_exponent}")
        print(f"  - Effective Capacity: {results['effective_capacity_As']/3600:.2f} Ah")
        print("=" * 60)


def main():
    print("Battery Discharge Simulation")
    print("Simulating real-world battery physics\n")

    battery = Batterysimulator(
        capacity_Ah=10,
        initial_soc=100,
        nominal_voltage=12    
    )

    print("Running simulation with constant 5A discharge for 3 hours...")
    results = battery.discharge_simulation(
        time_hours=3,
        current_profile='constant',
        current_value=5,
        add_noise=True
    )

    # Plotting results
    battery.plot_results(results, save_plot=True)
    
    # Additional example: Pulsed discharge
    print("\n" + "-" * 60)
    print("Running additional simulation with pulsed discharge...")
    print("-" * 60)
    
    results_pulsed = battery.discharge_simulation(
        time_hours=4,
        current_profile='pulsed',
        current_value=8,
        add_noise=True
    )
    
    # Creating comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.plot(results['time_hours'], results['SOC_percent'], 
            'b-', label='Constant 5A')
    ax1.plot(results_pulsed['time_hours'], results_pulsed['SOC_percent'], 
            'r-', label='Pulsed 8A')
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('SOC (%)')
    ax1.set_title('SOC Comparison: Different Discharge Profiles')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(results['time_hours'], results['current_A'], 
            'b-', alpha=0.7, label='Constant')
    ax2.plot(results_pulsed['time_hours'], results_pulsed['current_A'], 
            'r-', alpha=0.7, label='Pulsed')
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Current (A)')
    ax2.set_title('Current Profiles Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('comparison.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    main()