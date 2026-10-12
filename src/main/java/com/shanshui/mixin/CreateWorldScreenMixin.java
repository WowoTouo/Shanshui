package com.shanshui.mixin;

import com.shanshui.ShanshuiUI;
import com.shanshui.gui.createworld.ShanshuiApplier;
import com.shanshui.gui.createworld.ShanshuiState;
import com.shanshui.gui.createworld.ShanshuiTab;
import net.minecraft.client.gui.components.tabs.Tab;
import net.minecraft.client.gui.components.tabs.TabManager;
import net.minecraft.client.gui.components.toasts.SystemToast;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.io.IOException;
import java.util.Arrays;

/**
 * 界面注入：往创建世界界面的 TabBar 追加 Shanshui 标签页 + 创建时应用预设。
 * 与 UTF MixinCreateWorldScreen 同构：ModifyArg addTabs 数组扩容 + onCreate HEAD 拦截。
 */
@Mixin(CreateWorldScreen.class)
public abstract class CreateWorldScreenMixin extends Screen implements ShanshuiState.Holder {
    @Shadow
    @Final
    private WorldCreationUiState uiState;
    @Shadow
    @Final
    private TabManager tabManager;
    @Unique
    private ShanshuiState shanshui$state;

    protected CreateWorldScreenMixin(Component title) {
        super(title);
    }

    @Shadow
    protected abstract void onCreate();

    @Override
    public ShanshuiState shanshui$getState() {
        if (this.shanshui$state == null) {
            this.shanshui$state = new ShanshuiState((CreateWorldScreen) (Object) this, this.uiState);
        }
        return this.shanshui$state;
    }

    @ModifyArg(method = "init",
            at = @At(value = "INVOKE",
                    target = "Lnet/minecraft/client/gui/components/tabs/MenuTabBar$Builder;addTabs([Lnet/minecraft/client/gui/components/tabs/Tab;)Lnet/minecraft/client/gui/components/tabs/MenuTabBar$Builder;"))
    private Tab[] shanshui$addTab(Tab[] tabs) {
        Tab[] withShanshui = Arrays.copyOf(tabs, tabs.length + 1);
        withShanshui[tabs.length] = new ShanshuiTab((CreateWorldScreen) (Object) this);
        return withShanshui;
    }

    @Inject(method = "onCreate", at = @At("HEAD"), cancellable = true)
    private void shanshui$applyPreset(CallbackInfo ci) {
        ShanshuiState state = this.shanshui$getState();
        try {
            if (!ShanshuiApplier.prepareForCreate((CreateWorldScreen) (Object) this, state)) {
                ci.cancel();
            }
        } catch (IOException | RuntimeException e) {
            ShanshuiUI.LOGGER.error("Couldn't prepare the Shanshui preset", e);
            state.setPendingSelection(null);
            SystemToast.addOrUpdate(this.minecraft.gui.toastManager(), SystemToast.SystemToastId.PACK_LOAD_FAILURE,
                    Component.translatable("tab.shanshui.apply.failed"), Component.literal(String.valueOf(e.getMessage())));
            ci.cancel();
        }
    }

    @Inject(method = "tick", at = @At("HEAD"))
    private void shanshui$tick(CallbackInfo ci) {
        ShanshuiState state = this.shanshui$getState();
        if (this.tabManager.getCurrentTab() instanceof ShanshuiTab shanshuiTab) {
            shanshuiTab.tick();
        }
        if (ShanshuiApplier.isReadyToCreate(state)) {
            state.setPendingSelection(null);
            this.minecraft.schedule(() -> {
                if (this.minecraft.gui.screen() == (Object) this) {
                    this.onCreate();
                }
            });
        }
    }
}
