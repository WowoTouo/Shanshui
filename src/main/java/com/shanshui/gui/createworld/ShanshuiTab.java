package com.shanshui.gui.createworld;

import com.shanshui.settings.ShanshuiSettings;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.StringWidget;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.components.tabs.Tab;
import net.minecraft.client.gui.layouts.Layout;
import net.minecraft.client.gui.layouts.LayoutElement;
import net.minecraft.client.gui.navigation.ScreenRectangle;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;

/**
 * Shanshui 地形调度标签页：对应 UTF 的 TerrainTab。
 * 左列参数控件（掩码频率/区块大小/B引擎占比/边界模式/海平面/世界高度），右侧预留预览区（M3 加入）。
 */
public class ShanshuiTab implements Tab {
    private static final int PADDING = 8;
    private static final int ROW = 20;
    private static final int GAP = 4;

    private final CreateWorldScreen screen;
    private final ShanshuiState state;
    private final StringWidget status;
    private final Button advancedButton;
    private final List<AbstractWidget> controls = new ArrayList<>();
    private final TabLayout layout = new TabLayout(this);

    public ShanshuiTab(CreateWorldScreen screen) {
        this.screen = screen;
        this.state = ShanshuiState.of(screen);
        Minecraft mc = Minecraft.getInstance();

        this.status = new StringWidget(Component.empty(), mc.font);

        this.advancedButton = Button.builder(
                Component.translatable("tab.shanshui.advanced"),
                b -> {}).tooltip(Tooltip.create(Component.translatable("tab.shanshui.advanced.tip"))).build();

        rebuildControls();
    }

    private void rebuildControls() {
        controls.clear();
        ShanshuiSettings s = state.settings();

        // 掩码频率滑块（0.0005 ~ 0.01，对数手感用线性近似）
        controls.add(new SimpleSlider(0, 0, 0, 20,
                Component.translatable("tab.shanshui.freq"),
                (double) ((s.maskFrequency() - 0.0005f) / 0.0095f),
                v -> state.update(p -> new ShanshuiSettings(
                        (float) (0.0005 + v * 0.0095), p.maskOctaves(), p.bShare(), p.boundary(), p.seaLevel(), p.worldHeight()))));

        // 区块大小（firstOctave 档）
        controls.add(CycleButton.<Integer>builder(SimpleSlider::clampLabelComponent, s.maskOctaves())
                .withValues(-6, -5, -4, -3, -2)
                .create(0, 0, 0, 20, Component.translatable("tab.shanshui.size"),
                        (b, v) -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), v, p.bShare(), p.boundary(), p.seaLevel(), p.worldHeight()))));

        // B 引擎占比滑块（0~1）
        controls.add(new SimpleSlider(0, 0, 0, 20,
                Component.translatable("tab.shanshui.bshare"),
                s.bShare(),
                v -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), p.maskOctaves(), v.floatValue(), p.boundary(), p.seaLevel(), p.worldHeight()))));

        // 边界模式
        controls.add(CycleButton.<ShanshuiSettings.BoundaryMode>builder(b -> Component.literal(b.label), s.boundary())
                .withValues(ShanshuiSettings.BoundaryMode.values())
                .create(0, 0, 0, 20, Component.translatable("tab.shanshui.boundary"),
                        (b, v) -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), p.maskOctaves(), p.bShare(), v, p.seaLevel(), p.worldHeight()))));

        // 海平面滑块（-64 ~ 128）
        controls.add(new SimpleSlider(0, 0, 0, 20,
                Component.translatable("tab.shanshui.sea"),
                (double) (s.seaLevel() + 64) / 192.0,
                v -> state.update(p -> new ShanshuiSettings(p.maskFrequency(), p.maskOctaves(), p.bShare(), p.boundary(), Mth.floor(v * 192.0) - 64, p.worldHeight()))));

        // 世界高度（固定显示 4064 兜底）
        controls.add(new StringWidget(Component.translatable("tab.shanshui.height", s.worldHeight()), Minecraft.getInstance().font));
    }

    @Override
    public Component getTabTitle() {
        return Component.literal("Shanshui");
    }

    @Override
    public Component getTabExtraNarration() {
        return Component.empty();
    }

    @Override
    public void visitChildren(Consumer<AbstractWidget> consumer) {
        consumer.accept(this.status);
        consumer.accept(this.advancedButton);
        for (AbstractWidget w : this.controls) {
            consumer.accept(w);
        }
    }

    @Override
    public Layout getLayout() {
        return this.layout;
    }

    @Override
    public void doLayout(ScreenRectangle area) {
        this.layout.area = area;
        int columnWidth = Math.min(210, (area.width() - 24) / 2);
        int left = area.left() + (area.width() - columnWidth) / 2;
        int top = area.top() + PADDING;

        this.status.setX(left);
        this.status.setY(top);
        this.status.setMaxWidth(columnWidth);
        this.status.setHeight(12);
        updateLabels();

        int y = top + 16;
        this.advancedButton.setX(left);
        this.advancedButton.setY(y);
        this.advancedButton.setWidth(columnWidth);

        y += ROW + GAP;
        for (AbstractWidget w : this.controls) {
            w.setX(left);
            w.setY(y);
            w.setWidth(columnWidth);
            w.setHeight(20);
            y += ROW + GAP;
        }
    }

    public void tick() {
        updateLabels();
    }

    private void updateLabels() {
        ShanshuiSettings s = state.settings();
        if (state.active()) {
            this.status.setMessage(Component.translatable("tab.shanshui.active", s.boundary().label));
        } else {
            this.status.setMessage(Component.translatable("tab.shanshui.inactive"));
        }
    }

    /** 简易滑块：AbstractSliderButton 子类，值 0~1，变更回调。 */
    public static class SimpleSlider extends net.minecraft.client.gui.components.AbstractSliderButton {
        private final Consumer<Double> onChange;

        public SimpleSlider(int x, int y, int width, int height, Component label, double value, Consumer<Double> onChange) {
            super(x, y, width, height, label, Mth.clamp(value, 0.0, 1.0));
            this.onChange = onChange;
        }

        public static String clampLabel(Integer octaves) {
            return switch (octaves) {
                case -6 -> "超巨型";
                case -5 -> "巨型";
                case -4 -> "大";
                case -3 -> "中";
                default -> "小";
            };
        }

        public static Component clampLabelComponent(Integer octaves) {
            return Component.literal(clampLabel(octaves));
        }

        @Override
        protected void updateMessage() {
            setMessage(getMessage().copy().append(": ").append(String.format("%.3f", this.value)));
        }

        @Override
        protected void applyValue() {
            onChange.accept(this.value);
        }
    }

    private class TabLayout implements Layout {
        private ScreenRectangle area;
        final /* synthetic */ ShanshuiTab this$0;

        private TabLayout(ShanshuiTab tab) {
            Objects.requireNonNull(tab);
            this.this$0 = tab;
            this.area = ScreenRectangle.empty();
        }

        @Override
        public void visitChildren(Consumer<LayoutElement> consumer) {
            this.this$0.visitChildren(consumer::accept);
        }

        @Override
        public void removeChildren() {
        }

        @Override
        public void setX(int x) {
            int dx = x - this.area.left();
            this.visitChildren(child -> child.setX(child.getX() + dx));
            this.area = new ScreenRectangle(x, this.area.top(), this.area.width(), this.area.height());
        }

        @Override
        public void setY(int y) {
            int dy = y - this.area.top();
            this.visitChildren(child -> child.setY(child.getY() + dy));
            this.area = new ScreenRectangle(this.area.left(), y, this.area.width(), this.area.height());
        }

        @Override
        public int getX() {
            return this.area.left();
        }

        @Override
        public int getY() {
            return this.area.top();
        }

        @Override
        public int getWidth() {
            return this.area.width();
        }

        @Override
        public int getHeight() {
            return this.area.height();
        }
    }
}
