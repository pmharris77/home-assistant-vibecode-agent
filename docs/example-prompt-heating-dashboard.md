# Example Prompt: Heating Monitoring Dashboard

## The Prompt That Created "Heating Now" Dashboard

**User Request:**

```
Create a dashboard called "Heating Now" for monitoring my heating system.

Requirements:
1. Show boiler status and control:
   - Boiler power switch
   - Runtime in minutes
   - Current operation mode

2. Show cooldown status:
   - Remaining cooldown time

3. Show active heating summary:
   - How many TRVs are currently heating

4. Most importantly: Show thermostat controls for TRVs that are ACTIVELY HEATING right now
   - NOT all TRVs, only those currently in "heating" state
   - Use conditional cards that appear/disappear based on hvac_action
   - Each TRV should show as a thermostat card with full controls
   - Should dynamically update - when TRV starts heating, card appears

I have:
- 1 boiler switch: switch.boiler_zbminir2
- Boiler runtime sensor: sensor.boiler_runtime_minutes
- Operation mode: sensor.climate_operation_mode
- Cooldown sensor: sensor.adaptive_cooldown_remaining_minutes
- Active TRV count: sensor.active_trv_count
- 7 TRVs with climate entities and hvac_action sensors:
  * climate.sonoff_trvzb_thermostat + sensor.sonoff_trvzb_hvac_action
  * climate.sonoff_trvzb_thermostat_2 + sensor.sonoff_trvzb_hvac_action_2
  * climate.sonoff_trvzb_thermostat_3 + sensor.sonoff_trvzb_hvac_action_3
  * climate.kitchen_trv_thermostat + sensor.kitchen_trv_hvac_action
  * climate.bedroom_trv_thermostat + sensor.bedroom_trv_hvac_action
  * climate.alex_trv_thermostat + sensor.alex_trv_hvac_action
  * climate.bathroom_trv_thermostat + sensor.bathroom_trv_hvac_action

The key requirement: TRV thermostat cards should ONLY be visible when that specific TRV's hvac_action sensor shows "heating". If idle or off, the card should be hidden.

Save as: heating-now.yaml
```

---

## What AI Will Create

**Dashboard Structure:**

1. **🔥 Boiler Status Card**
   - Entity list card
   - Switch for manual control
   - Runtime monitoring
   - Operation mode display

2. **⏱️ Cooldown Status Card**
   - Entity list card
   - Remaining cooldown time

3. **📊 Active Heating Card**
   - Entity list card
   - Counter showing how many TRVs are heating

4. **🌡️ Dynamic TRV Controls (7 conditional cards)**
   - Each TRV wrapped in conditional card
   - Condition: `sensor.xxx_hvac_action == 'heating'`
   - Card type: `thermostat` (full temperature control)
   - Automatically shows/hides based on heating state

---

## Key Technical Features

**Conditional Cards:**
```yaml
- type: conditional
  conditions:
    - entity: sensor.bedroom_trv_hvac_action
      state: heating
  card:
    type: thermostat
    entity: climate.bedroom_trv_thermostat
    name: Bedroom (HEATING)
```

**Why This Works:**
- ✅ Shows only actively heating TRVs
- ✅ Real-time updates (card appears when heating starts)
- ✅ Clean UI (no clutter from idle TRVs)
- ✅ Full thermostat controls when visible
- ✅ Energy monitoring (see which rooms are heating)

---

## Alternative Simpler Prompt

If you don't know exact entity names:

```
Create a "Heating Now" dashboard for my heating system that shows:

1. Boiler status and control (find my boiler switch and runtime sensor)
2. Cooldown timer (find cooldown sensor)
3. Count of actively heating TRVs
4. Thermostat controls ONLY for TRVs that are currently heating (not idle ones)
   - Use conditional cards based on hvac_action sensor
   - Each TRV should have its own thermostat card
   - Cards should appear/disappear automatically based on heating state

I have 7 TRV thermostats with hvac_action sensors.
Save as heating-now.yaml
```

**AI will:**
1. Analyze your entities
2. Find boiler, sensors, TRVs automatically
3. Create conditional cards for each TRV
4. Apply the dashboard

---

## Result

**Single-view dashboard perfect for:**
- ✅ Real-time heating monitoring
- ✅ Quick boiler control
- ✅ Seeing which rooms are actively heating
- ✅ Adjusting temperature of heating rooms
- ✅ Understanding system state at a glance

**Dynamic behavior:**
- No TRVs heating → Shows only status cards
- 1 TRV heating → Shows boiler + 1 thermostat
- All TRVs heating → Shows boiler + 7 thermostats
- Automatic updates in real-time

---

*This prompt demonstrates AI-driven dashboard generation with conditional logic and dynamic UI elements.*




