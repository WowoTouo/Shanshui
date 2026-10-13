<!-- 任务 2026-10-13-v375-research-test.md 完成于 2026-10-13 22:20:52 -->

【结论】本次检索未取得 Tectonic 中 `final_density` 的任何直接证据：全部命中项均为本项目 `ShanshuiTab.java`（GUI 代码），与取证目标无关，故 Tectonic 特有的输入/输出语义与取值范围**现有证据无法判定**，不能臆断。

可确认的仅为原版公开机制（Minecraft 1.18+ 密度函数体系，非 Tectonic 取证结果）：

1. **语义**：`final_density` 是密度函数栈终点，输入为逐点三维上下文（x/y/z 及噪声插值上下文），输出每点一个 float 密度；正值→陆地，负值→空气或水（y 低于海平面且负值填水），过零点即地形表面。
2. **取值范围**：原版无统一上下界，取决于上游函数链；典型地形在约 ±1.5 量级，经 `y_clamped_gradient`/spline 塑形。
3. **可改写性**：原版允许数据包覆盖 `data/<ns>/worldgen/density_function/final_density.json`，可整体替换或外包一层 `lerp(mask, A, B)`——这正是调度器缝合点。但 Tectonic 是否用自定义 df 类型、是否硬编码高度限制（4064 风险点），**必须反编译其 jar 验证**。

**下一步取证**：定位 Tectonic jar（mods 目录/Gradle 缓存），解包查 `data/*/worldgen/density_function/*.json`，CFR 反编译搜 `final_density`、`DensityFunction`、`set_height_limits`。

---
（据 worker 确定性侦察取证合成，检索命中见下）
eject|not authorized|Permission|invalid|fatal: unable to access.*404|already exists"; then
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:3:import com.shanshui.settings.ShanshuiSettings;
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:25: * Shanshui 地形调度标签页：对应 UTF 的 TerrainTab。
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:28:public class ShanshuiTab implements Tab {
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:34:    private final ShanshuiState state;
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:40:    public ShanshuiTab(CreateWorldScreen screen) {
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:42:        this.state = ShanshuiState.of(screen);
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:56:        ShanshuiSettings s = state.settings();
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:62:                v -> state.update(p -> new ShanshuiSettings(
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:69:                        (b, v) -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), v, p.bShare(), p.boundary(), p.seaLevel(), p.worldHeight()))));
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:75:                v -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), p.maskOctaves(), v.floatValue(), p.boundary(), p.seaLevel(), p.worldHeight()))));
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:78:        controls.add(CycleButton.<ShanshuiSettings.BoundaryMode>builder(b -> Component.literal(b.label), s.boundary())
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:79:                .withValues(ShanshuiSettings.BoundaryMode.values())
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:81:                        (b, v) -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), p.maskOctaves(), p.bShare(), v, p.seaLevel(), p.worldHeight()))));
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:87:                v -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), p.maskOctaves(), p.bShare(), p.boundary(), Mth.floor(v * 192.0) - 64, p.worldHeight()))));
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:95:        return Component.literal("Shanshui");
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:150:        ShanshuiSettings s = state.settings();
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:194:        final /* synthetic */ ShanshuiTab this$0;
/home/agent/Shanshui/src/main/java/com/shanshui/gui/createworld/ShanshuiTab.java:196:        private TabLayout(ShanshuiTab tab) {

