# Plasma Forge Power · 锻炉与聚变分色功率控制

[English](README.en.md) · **Minecraft 1.7.10 / GTNH 2.9.0-RC-2**

由 GPT-6（Codex）实现。为原有控制器增加蓝白色配置界面，让不同颜色的输入组使用各自的功率上限。无需替换控制器，无需给能源仓染色。

**0.2.0-alpha** 新增普通聚变 Mk-I～Mk-V 和压缩聚变 Mk-I～Mk-V。[聚变用法](docs/FUSION.md)。

<p align="center"><strong>一台锻炉，按输入颜色管理功率</strong><br>17 个输入组 · 原生界面 · 配置复制 · 自动校验</p>

<p align="center">
  <a href="https://github.com/arturia-Xayah/gtnh-plasma-forge-power/releases/tag/v0.2.0-alpha-GTNH-2.9.0-RC-2"><img alt="Download" src="https://img.shields.io/badge/Download-0.2.0--alpha-176aab?style=for-the-badge"></a>
  <img alt="GTNH version" src="https://img.shields.io/badge/GTNH-2.9.0--RC--2-536d82?style=for-the-badge">
  <img alt="Minecraft" src="https://img.shields.io/badge/Minecraft-1.7.10-536d82?style=for-the-badge">
  <a href="https://github.com/arturia-Xayah/gtnh-plasma-forge-power/actions/workflows/build.yml"><img alt="Build" src="https://github.com/arturia-Xayah/gtnh-plasma-forge-power/actions/workflows/build.yml/badge.svg"></a>
</p>

<p align="center"><a href="https://github.com/arturia-Xayah/gtnh-plasma-forge-power/releases/tag/v0.2.0-alpha-GTNH-2.9.0-RC-2">下载 JAR</a> · <a href="README.en.md">English</a> · <a href="VERIFICATION.md">验证记录</a></p>

![颜色功率设置界面](previews/red-manual.png)

> 按当前界面布局生成的离线预览。游戏内字体和缩放由客户端设置决定。

## 使用

1. 将 `plasmaforgepower-0.2.0-alpha-GTNH-2.9.0-RC-2.jar` 放入 `mods`。联机时服务器和客户端安装相同版本。
2. 打开锻炉或聚变主机，点击右侧蓝色 **P** 按钮。
3. 左侧选择输入仓、输入总线或输入总成的染色颜色；未染色使用“无色”。
4. 输入最大 A 数，选择电压单位（**ULV～MAX**，含 LuV / ZPM / UV），点击“保存设置”。

例如，一个 1024A UMV 能源仓可以同时作为下列配置的统一电源：

| 输入组 | 配置 | 含义 |
|---|---|---|
| 红色 | 1A UEV | 按不超过 8,388,608 EU/t 的预算计算配方 |
| 绿色 | 16A UMV | 按不超过 2,147,483,648 EU/t 的预算计算配方 |
| 无色 | -1 | 使用原版整机功率规则 |

**0 和 -1 都表示自动。** 支持小数 A，换算时向下取整到整数 EU/t；电压是功率换算单位，不改变能源仓的物理电压。功率上限是允许使用的最大值，实际耗电取决于配方和离散超频结果。

界面顶部同时显示整机供电上限及其等效电流、电压，例如 `≈1.37×10^11 EU/t (1024A UMV)`。A 数按整机供电功率除以原版平均输入电压计算；不能整除时显示近似值。达到 10 亿 EU/t 时，功率采用约 3 位有效数字的科学计数法；悬停显示完整精确 EU/t，仅改变显示。

## 生效规则

- 配方资格、超频、适用的并行和聚合模式额外催化剂计算使用同一功率预算。
- 设置在下一轮配方生效，正在运行的配方保持其已有耗电和时长。
- 保存时，超出已成型锻炉供电能力的设置会被下调并保存。
- 更换能源仓后，成功检测成型时重新校验。手动上限下调后，不会随着换回大能源仓自动上升。
- 未成型、缺能源仓或正在复制施工时保留配置，成功成型后再校验。
- “自动”遵守原版规则，包括普通单能源仓的原生处理限制；本 Mod 不增加实际供电能力。
- 全部组均为自动时，直接使用原版配方检查流程。

锻炉的有色组可以使用原版允许的无色公共原料。有手动限制时，完整的无色配方先按无色组计算，再尝试完整的有色配方，最后尝试需要公共原料补充的有色配方。完整无色配方不能借空的有色仓绕过自己的上限。输入分离开启时保留总线分离规则。

同一输入总成中的所有内部配方槽使用该总成的颜色。染色并不会让一台锻炉同时执行多个不同配方。

## 复制与保存

- 支持物质操纵者的 GT 配置采集、复制及堆叠所用的 `IDataCopyable` 路径。
- 支持数据宝珠的原生多方块配置复制：左键主机保存，右键目标主机粘贴。
- 复制的是 17 个输入组的设置，不复制配方进度、能源或物品。
- 已成型目标会立即校验并下调超限值；未成型目标完整保留设置，等待成功成型。
- 设置保存在原控制器的独立 NBT 字段中，支持服务器重启。

## 聚变与压缩聚变（0.2.0）

在主机原生界面点击 **P** 使用同一套设置。聚变显示的是原生处理功率上限，仍保留能源缓存、启动能量门槛、充电速率与连续运行规则。启动能量是 EU，运行功率是 EU/t，两者独立。设置只影响下一轮配方；不主动中断反应，不额外扣热切换启动能量。

按当前选择，**仅限功率，保留原版选配方顺序**。不会自动优先下单配方；若常驻配方原料一直充足，原生缓存和遍历仍可能继续选择它。需要用现有投料控制让机器选中目标配方。预算小于配方基础 EU/t 时会拒绝该候选，不会把配方降到基础耗电以下。

[详细用法与范围](docs/FUSION.md) · [后台验证](VERIFICATION.md)

## 兼容性与移除

目标环境：**GTNH 2.9.0-RC-2、GregTech 5.09.54.205、ModularUI 2.3.92、UniMixins 0.3.1**。这些依赖已在对应整合包中，不包含在本 Mod JAR 内。其他 GT 版本需要验证补丁位置后再使用。

Mod 不新增注册方块或物品。移除前等待当前配方完成，关闭锻炉，保存并退出服务器或游戏，再移除客户端和服务器上的 Mod。移除后控制器和结构保留，功率计算恢复原版；额外设置可能在原版保存后丢失。

后台测试覆盖真实结构成型、配方、逐 tick 运行、原料保护、换仓、物质操纵者、数据宝珠、重启和移除。客户端未启动，实际画面与鼠标操作尚未在游戏客户端验收；详细范围见 [VERIFICATION.md](VERIFICATION.md)。

## 构建

使用 JDK 25 运行 Gradle；构建工具还需要 Java 8 工具链编译 Minecraft 基础代码。

```sh
./gradlew build
```

安装文件是 `build/libs/plasmaforgepower-0.2.0-alpha.jar`，不要安装 `-dev.jar` 或 `-sources.jar`。发布目录中的安装文件会额外标明 GTNH 版本。

集成测试源码位于 `src/packTest`，只在 `-PforgePowerTests=true` 时加入，正常安装包不含测试 Mod。测试方式见 [TESTING.md](TESTING.md)。

LGPL-3.0-or-later。相关上游接口见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
