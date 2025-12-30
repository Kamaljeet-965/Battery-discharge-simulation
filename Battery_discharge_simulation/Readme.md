# Battery Discharge Simulation (Physics-Based)

This project models the discharge behavior of a battery using
first-principles physics rather than curve fitting.

## What the Model Does
- Tracks State of Charge (SOC) using coulomb counting
- Simulates realistic discharge current variations
- Calculates terminal voltage under load
- Computes power delivery over time
- Includes low-voltage and SOC warning thresholds

## Physics Used
- Charge balance:
  SOC(t) = SOC₀ − (1/C) ∫ I(t) dt
- Terminal voltage:
  V = V_oc(SOC) − I·R_internal
- Power:
  P = V · I

## Assumptions
- Constant temperature
- Lumped-parameter battery model
- Fixed internal resistance
- No aging or thermal effects

## Tools Used
- Python
- NumPy
- Matplotlib

## Output
The simulation generates:
- SOC vs Time
- Discharge Current Profile
- Terminal Voltage vs Time
- Power Delivery vs Time

## Future Improvements
- Temperature-dependent behavior
- SOC-dependent internal resistance
- Battery aging effects
