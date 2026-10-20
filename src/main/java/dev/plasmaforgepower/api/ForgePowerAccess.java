package dev.plasmaforgepower.api;

import dev.plasmaforgepower.core.PowerSettings;
import gregtech.api.util.GTRecipe;

/** Added only to the existing DTPF controller; there are no new registered blocks or inventory items. */
public interface ForgePowerAccess {

    PowerSettings pfp$getSettings();

    int pfp$applySettings(PowerSettings settings);

    long pfp$ratedPower();

    long pfp$ratedVoltage();

    boolean pfp$isFormed();

    int pfp$activeColor();

    long pfp$attemptPower();

    boolean pfp$sourceAllowed(GTRecipe recipe);
}
