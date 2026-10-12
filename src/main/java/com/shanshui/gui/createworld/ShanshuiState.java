package com.shanshui.gui.createworld;

import com.shanshui.settings.ShanshuiSettings;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;

import java.util.List;
import java.util.function.Consumer;

/**
 * Shanshui 地形状态：持有当前参数集 + 修订号 + 待应用数据包列表。
 * 对应 UTF 的 TerrainState。
 */
public class ShanshuiState {
    public interface Holder {
        ShanshuiState shanshui$getState();
    }

    private final CreateWorldScreen screen;
    private final WorldCreationUiState uiState;
    private ShanshuiSettings settings = ShanshuiSettings.DEFAULT;
    private int revision;
    private boolean active = true;
    private List<String> pendingSelection;

    public ShanshuiState(CreateWorldScreen screen, WorldCreationUiState uiState) {
        this.screen = screen;
        this.uiState = uiState;
    }

    public static ShanshuiState of(CreateWorldScreen screen) {
        return ((Holder) (Object) screen).shanshui$getState();
    }

    public CreateWorldScreen screen() {
        return this.screen;
    }

    public WorldCreationUiState uiState() {
        return this.uiState;
    }

    public ShanshuiSettings settings() {
        return this.settings;
    }

    /** 参数变更入口：变更后 revision++，驱动界面刷新。 */
    public void update(Consumer<ShanshuiSettings> change) {
        ShanshuiSettings next = new ShanshuiSettings(
                this.settings.maskFrequency(),
                this.settings.maskOctaves(),
                this.settings.bShare(),
                this.settings.boundary(),
                this.settings.seaLevel(),
                this.settings.worldHeight());
        change.accept(next);
        this.settings = next;
        this.revision++;
    }

    public int revision() {
        return this.revision;
    }

    public boolean active() {
        return this.active;
    }

    public void setActive(boolean active) {
        this.active = active;
        this.revision++;
    }

    public List<String> pendingSelection() {
        return this.pendingSelection;
    }

    public void setPendingSelection(List<String> pendingSelection) {
        this.pendingSelection = pendingSelection;
    }
}
