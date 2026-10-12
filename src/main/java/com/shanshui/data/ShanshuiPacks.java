package com.shanshui.data;

import com.shanshui.ShanshuiUI;
import com.shanshui.settings.ShanshuiSettings;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.Enumeration;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

/**
 * Shanshui 数据包生成器：对应 UTF 的 PresetPacks。
 * 把模板（zz_hybrid_scheduler v3）按参数替换占位符，打包成 zip 数据包。
 * 模板结构（与 v3 一致）：
 *   pack.mcmeta
 *   data/hybrid/worldgen/noise/region_mask.json        {{maskOctaves}}
 *   data/hybrid/worldgen/density_function/region_mask.json {{maskFrequency}}
 *   data/minecraft/dimension_type/overworld.json       {{worldHeight}}/{{worldDepth}}
 *   data/minecraft/worldgen/noise_settings/overworld.json {{seaLevel}}/{{worldDepth}}
 */
public class ShanshuiPacks {
    public static final String PACK_PREFIX = "shanshui-preset";

    /** 参数 JSON → SHA-1 前 12 位 → 数据包文件名（同 PresetApplier.packName）。 */
    public static String packName(ShanshuiSettings settings) {
        String json = settings.serialize();
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-1");
            byte[] hash = md.digest(json.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return PACK_PREFIX + "-" + sb.substring(0, 12) + ".zip";
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    public static boolean isShanshuiPack(String packId) {
        return packId.startsWith("file/" + PACK_PREFIX) && packId.endsWith(".zip");
    }

    /** 生成数据包 zip 到目标路径。 */
    public static void export(ShanshuiSettings settings, Path zip) throws IOException {
        Path workDir = Files.createTempDirectory("shanshui-preset-");
        try {
            Path generated = workDir.resolve("pack");
            renderTemplates(settings, generated);
            Path parent = zip.toAbsolutePath().getParent();
            Files.createDirectories(parent);
            Path partial = Files.createTempFile(parent, "shanshui-preset-", ".zip.tmp");
            Files.delete(partial);
            zipDirectory(generated, partial);
            Files.move(partial, zip, StandardCopyOption.REPLACE_EXISTING);
        } finally {
            deleteRecursive(workDir);
        }
        ShanshuiUI.LOGGER.info("Wrote Shanshui preset datapack to {}", zip);
    }

    /** 渲染模板：占位符替换 → 写入 generated 目录。 */
    private static void renderTemplates(ShanshuiSettings s, Path out) throws IOException {
        String[] entries = {
                "pack.mcmeta",
                "data/hybrid/worldgen/noise/region_mask.json",
                "data/hybrid/worldgen/density_function/region_mask.json",
                "data/hybrid/worldgen/density_function/mask01.json",
                "data/hybrid/worldgen/density_function/final_density.json",
                "data/hybrid/worldgen/density_function/vanilla/base_3d_noise.json",
                "data/hybrid/worldgen/density_function/vanilla/chunk_surface_level.json",
                "data/hybrid/worldgen/density_function/vanilla/continents.json",
                "data/hybrid/worldgen/density_function/vanilla/depth.json",
                "data/hybrid/worldgen/density_function/vanilla/erosion.json",
                "data/hybrid/worldgen/density_function/vanilla/factor.json",
                "data/hybrid/worldgen/density_function/vanilla/final_density.json",
                "data/hybrid/worldgen/density_function/vanilla/jaggedness.json",
                "data/hybrid/worldgen/density_function/vanilla/offset.json",
                "data/hybrid/worldgen/density_function/vanilla/preliminary_surface_level.json",
                "data/hybrid/worldgen/density_function/vanilla/ridges.json",
                "data/hybrid/worldgen/density_function/vanilla/ridges_folded.json",
                "data/hybrid/worldgen/density_function/vanilla/sloped_cheese.json",
                "data/hybrid/worldgen/density_function/vanilla/temperature.json",
                "data/hybrid/worldgen/density_function/vanilla/vegetation.json",
                "data/hybrid/worldgen/density_function/vanilla/caves/entrances.json",
                "data/hybrid/worldgen/density_function/vanilla/caves/noodle.json",
                "data/hybrid/worldgen/density_function/vanilla/caves/pillars.json",
                "data/hybrid/worldgen/density_function/vanilla/caves/spaghetti_2d.json",
                "data/hybrid/worldgen/density_function/vanilla/caves/spaghetti_2d_thickness_modulator.json",
                "data/hybrid/worldgen/density_function/vanilla/caves/spaghetti_roughness_function.json",
                "data/hybrid/worldgen/density_function/vanilla/ore_vein/copper_density.json",
                "data/hybrid/worldgen/density_function/vanilla/ore_vein/gap.json",
                "data/hybrid/worldgen/density_function/vanilla/ore_vein/iron_density.json",
                "data/hybrid/worldgen/density_function/vanilla/ore_vein/mask.json",
                "data/hybrid/worldgen/density_function/vanilla/ore_vein/richness.json",
                "data/hybrid/worldgen/density_function/vanilla/ore_vein/toggle.json",
                "data/minecraft/dimension_type/overworld.json",
                "data/minecraft/worldgen/noise_settings/overworld.json"
        };
        for (String entry : entries) {
            Path target = out.resolve(entry);
            Files.createDirectories(target.getParent());
            String content = readResource("/templates/zz_hybrid_scheduler/" + entry);
            content = content
                    .replace("{{maskFrequency}}", formatFloat(s.maskFrequency()))
                    .replace("{{maskOctaves}}", Integer.toString(s.maskOctaves()))
                    .replace("{{seaLevel}}", Integer.toString(s.seaLevel()))
                    .replace("{{worldHeight}}", Integer.toString(s.worldHeight()))
                    .replace("{{worldDepth}}", Integer.toString(-(s.worldHeight() / 2)));
            Files.write(target, content.getBytes(StandardCharsets.UTF_8));
        }
    }

    private static String formatFloat(float f) {
        if (f == Math.floor(f) && !Float.isInfinite(f)) {
            return Integer.toString((int) f);
        }
        return Float.toString(f);
    }

    private static String readResource(String path) throws IOException {
        try (InputStream in = ShanshuiPacks.class.getResourceAsStream(path)) {
            if (in == null) {
                throw new IOException("Template not found: " + path);
            }
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    /** 目录 → zip（jar: URI 方式，同 PresetPacks.zip）。 */
    private static void zipDirectory(Path dir, Path zip) throws IOException {
        URI uri = URI.create("jar:" + zip.toUri());
        try (FileSystem fs = FileSystems.newFileSystem(uri, Map.of("create", "true"))) {
            Path root = fs.getPath("/");
            Files.walk(dir).forEach(p -> {
                if (p.equals(dir)) return;
                try {
                    Path target = root.resolve(dir.relativize(p).toString());
                    if (Files.isDirectory(p)) {
                        Files.createDirectories(target);
                    } else {
                        Files.copy(p, target, StandardCopyOption.REPLACE_EXISTING);
                    }
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });
        }
    }

    private static void deleteRecursive(Path dir) {
        if (dir == null || !Files.exists(dir)) return;
        try (var walk = Files.walk(dir)) {
            walk.sorted(java.util.Comparator.reverseOrder()).forEach(p -> {
                try {
                    Files.deleteIfExists(p);
                } catch (IOException ignored) {
                }
            });
        } catch (IOException ignored) {
        }
    }

    private ShanshuiPacks() {
    }
}
