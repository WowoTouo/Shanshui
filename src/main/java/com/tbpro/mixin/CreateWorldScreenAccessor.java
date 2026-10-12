package com.tbpro.mixin;

import com.mojang.datafixers.util.Pair;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.server.packs.repository.PackRepository;
import net.minecraft.world.level.WorldDataConfiguration;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

import java.nio.file.Path;
import java.util.function.Consumer;

/**
 * Accessor：暴露 CreateWorldScreen 的私有数据包操作（UTF 内部同款机制）。
 */
@Mixin(CreateWorldScreen.class)
public interface CreateWorldScreenAccessor {
    @Invoker("getDataPackSelectionSettings")
    Pair<Path, PackRepository> tbpro$getDataPackSelectionSettings(WorldDataConfiguration config);

    @Invoker("tryApplyNewDataPacks")
    void tbpro$tryApplyNewDataPacks(PackRepository repository, boolean requireSelected, Consumer<WorldDataConfiguration> onReload);
}
