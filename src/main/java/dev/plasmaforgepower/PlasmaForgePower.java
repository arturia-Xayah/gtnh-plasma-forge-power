package dev.plasmaforgepower;

import java.util.Map;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.network.NetworkCheckHandler;
import cpw.mods.fml.relauncher.Side;

@Mod(
    modid = PlasmaForgePower.ID,
    name = "Plasma Forge Power",
    version = Tags.VERSION,
    dependencies = "required-after:gregtech;required-after:modularui2;required-after:unimixins",
    acceptedMinecraftVersions = "[1.7.10]")
public final class PlasmaForgePower {

    public static final String ID = "plasmaforgepower";

    @NetworkCheckHandler
    public boolean compatible(Map<String, String> remoteVersions, Side remoteSide) {
        return Tags.VERSION.equals(remoteVersions.get(ID));
    }
}
