package com.tbpro.mixin;

import com.tbpro.TbproUI;
import com.tbpro.gui.createworld.TbproApplier;
import com.tbpro.gui.createworld.TbproState;
import com.tbpro.gui.createworld.TbproTab;
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
 * 界面注入：往创建世界界面的 TabBar 追加 TBPRO 标签页 + 创建时应用预设。
 * 与 UTF MixinCreateWorldScreen 同构：ModifyArg addTabs 数组扩容 + onCreate HEAD 拦截。
 */
@Mixin(CreateWorldScreen.class)
public abstract class CreateWorldScreenMixin extends Screen implements TbproState.Holder {
    @Shadow
    @Final
    private WorldCreationUiState uiState;
    @Shadow
    @Final
    private TabManager tabManager;
    @Unique
    private TbproState tbpro$state;

    protected CreateWorldScreenMixin(Component title) {
        super(title);
    }

    @Shadow
    protected abstract void onCreate();

    @Override
    public TbproState tbpro$getState() {
        if (this.tbpro$state == null) {
            this.tbpro$state = new TbproState((CreateWorldScreen) (Object) this, this.uiState);
        }
        return this.tbpro$state;
    }

    @ModifyArg(method = "init",
            at = @At(value = "INVOKE",
                    target = "Lnet/minecraft/client/gui/components/tabs/MenuTabBar$Builder;addTabs([Lnet/minecraft/client/gui/components/tabs/Tab;)Lnet/minecraft/client/gui/components/tabs/MenuTabBar$Builder;"))
    private Tab[] tbpro$addTab(Tab[] tabs) {
        Tab[] withTbpro = Arrays.copyOf(tabs, tabs.length + 1);
        withTbpro[tabs.length] = new TbproTab((CreateWorldScreen) (Object) this);
        return withTbpro;
    }

    @Inject(method = "onCreate", at = @At("HEAD"), cancellable = true)
    private void tbpro$applyPreset(CallbackInfo ci) {
        TbproState state = this.tbpro$getState();
        try {
            if (!TbproApplier.prepareForCreate((CreateWorldScreen) (Object) this, state)) {
                ci.cancel();
            }
        } catch (IOException | RuntimeException e) {
            TbproUI.LOGGER.error("Couldn't prepare the TBPRO preset", e);
            state.setPendingSelection(null);
            SystemToast.addOrUpdate(this.minecraft.gui.toastManager(), SystemToast.SystemToastId.PACK_LOAD_FAILURE,
                    Component.translatable("tab.tbpro.apply.failed"), Component.literal(String.valueOf(e.getMessage())));
            ci.cancel();
        }
    }

    @Inject(method = "tick", at = @At("HEAD"))
    private void tbpro$tick(CallbackInfo ci) {
        TbproState state = this.tbpro$getState();
        if (this.tabManager.getCurrentTab() instanceof TbproTab tbproTab) {
            tbproTab.tick();
        }
        if (TbproApplier.isReadyToCreate(state)) {
            state.setPendingSelection(null);
            this.minecraft.schedule(() -> {
                if (this.minecraft.gui.screen() == (Object) this) {
                    this.onCreate();
                }
            });
        }
    }
}
