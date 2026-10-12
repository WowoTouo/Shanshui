package com.shanshui.gui.createworld;

import com.mojang.datafixers.util.Pair;
import com.shanshui.ShanshuiUI;
import com.shanshui.data.ShanshuiPacks;
import com.shanshui.mixin.CreateWorldScreenAccessor;
import com.shanshui.settings.ShanshuiSettings;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.server.packs.repository.PackRepository;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

/**
 * Shanshui 预设应用器：对应 UTF 的 PresetApplier。
 * 创建世界时：参数 → zip 数据包 → 注入 MC 数据包临时目录 → 选中 → 重载 → 按参数生成。
 */
public final class ShanshuiApplier {

    public static boolean prepareForCreate(CreateWorldScreen screen, ShanshuiState state) throws IOException {
        CreateWorldScreenAccessor accessor = (CreateWorldScreenAccessor) (Object) screen;
        Pair<Path, PackRepository> dataPacks =
                accessor.shanshui$getDataPackSelectionSettings(state.uiState().getSettings().dataConfiguration());
        Path directory = dataPacks.getFirst();
        PackRepository repository = dataPacks.getSecond();

        List<String> current = state.uiState().getSettings().dataConfiguration().dataPacks().getEnabled();
        String wanted = state.active() ? ShanshuiPacks.packName(state.settings()) : null;
        List<String> wantedPacks = wanted != null ? List.of("file/" + wanted) : List.of();

        if (presetPacks(current).equals(wantedPacks)) {
            return true;
        }

        List<String> selection = new ArrayList<>(current.stream()
                .filter(id -> !ShanshuiPacks.isShanshuiPack(id)).toList());
        selection.addAll(wantedPacks);

        if (wanted != null && !Files.exists(directory.resolve(wanted))) {
            ShanshuiPacks.export(state.settings(), directory.resolve(wanted));
        }
        deleteOtherPacks(directory, wanted);

        repository.reload();
        repository.setSelected(selection);
        if (wanted != null && !repository.getSelectedIds().contains("file/" + wanted)) {
            throw new IOException("The Shanshui datapack " + wanted + " wasn't found in " + directory);
        }

        state.setPendingSelection(List.copyOf(selection));
        accessor.shanshui$tryApplyNewDataPacks(repository, false, config -> state.setPendingSelection(null));
        return false;
    }

    public static boolean isReadyToCreate(ShanshuiState state) {
        List<String> pending = state.pendingSelection();
        return pending != null && presetPacks(state.uiState().getSettings().dataConfiguration().dataPacks().getEnabled())
                .equals(presetPacks(pending));
    }

    private static List<String> presetPacks(List<String> packs) {
        return packs.stream().filter(ShanshuiPacks::isShanshuiPack).toList();
    }

    private static void deleteOtherPacks(Path directory, String keep) throws IOException {
        if (!Files.isDirectory(directory)) {
            return;
        }
        try (Stream<Path> files = Files.list(directory)) {
            List<Path> stale = files.filter(file -> {
                String name = file.getFileName().toString();
                return name.startsWith(ShanshuiPacks.PACK_PREFIX) && name.endsWith(".zip") && !name.equals(keep);
            }).toList();
            for (Path f : stale) {
                Files.deleteIfExists(f);
            }
        }
    }

    private ShanshuiApplier() {
    }
}
