# Upstream interfaces

This project uses, but does not bundle, the following upstream projects:

- [GT5-Unofficial 5.09.54.205](https://github.com/GTNewHorizons/GT5-Unofficial/tree/5.09.54.205): original forge, ordinary / compact fusion, overclocking, hatch and configuration-copy APIs. LGPL-3.0.
- [ModularUI 2](https://github.com/GTNewHorizons/ModularUI): native widgets and synchronized panels. LGPL-3.0.
- [UniMixins](https://github.com/LegacyModdingMC/UniMixins): late mixin loading and runtime patching. Consult the upstream repository for its modules' licenses.
- [Matter Manipulator 0.1.61-GTNH](https://github.com/GTNewHorizons/MatterManipulator/tree/0.1.61-GTNH): optional native configuration-copy integration, exercised in the dedicated-server fixture. No Matter Manipulator code is bundled.
- GTNH Convention / ExampleMod Gradle build templates supplied by the GTNH build ecosystem.

The input router preserves GT's public inventory and recipe interfaces, shared-input convention, and native recipe processing. The product interface uses native ModularUI drawing primitives; it does not include GTO artwork or an embedded web browser.

The inherited ExampleMod build templates retain the [ExampleMod MIT notice](LICENSES/ExampleMod-MIT.txt). The LGPL license incorporates the [GNU GPL v3 text](LICENSES/GPL-3.0.txt).
