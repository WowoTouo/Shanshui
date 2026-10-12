package com.shanshui.settings;

/**
 * Shanshui 调度器参数模型。
 * 与 UTF 的 Preset record 同理：一个参数集 → 序列化 → 生成数据包。
 * 序列化用手写 JSON（避免引入 Mojang codec 依赖链），格式：
 * {"maskFrequency":0.002,"maskOctaves":-4,"bShare":0.5,"boundary":"GRADIENT","seaLevel":63,"worldHeight":4064}
 */
public record ShanshuiSettings(
        float maskFrequency,
        int maskOctaves,
        float bShare,
        BoundaryMode boundary,
        int seaLevel,
        int worldHeight
) {
    public enum BoundaryMode {
        GRADIENT("渐变过渡"),
        CLIFF("自然悬崖"),
        SEA_MASK("海面掩蔽"),
        NEIGHBOR_AVG("邻区均值");

        public final String label;

        BoundaryMode(String label) {
            this.label = label;
        }

        public static BoundaryMode from(String name) {
            for (BoundaryMode m : values()) {
                if (m.name().equalsIgnoreCase(name)) {
                    return m;
                }
            }
            return GRADIENT;
        }
    }

    public static final ShanshuiSettings DEFAULT = new ShanshuiSettings(
            0.002f,   // maskFrequency：与 zz_hybrid_scheduler v3 一致
            -4,       // maskOctaves：firstOctave（大区块）
            0.5f,     // bShare：B 引擎(山区)占比倾向
            BoundaryMode.GRADIENT,
            63,       // seaLevel：原版默认，用户要求海平面当世界基础线
            4064      // worldHeight：用户硬性要求
    );

    public ShanshuiSettings {
        if (maskFrequency < 0.0001f || maskFrequency > 0.1f) {
            maskFrequency = DEFAULT.maskFrequency();
        }
        if (maskOctaves > 0) {
            maskOctaves = DEFAULT.maskOctaves();
        }
        if (bShare < 0.0f || bShare > 1.0f) {
            bShare = DEFAULT.bShare();
        }
        if (seaLevel < -64 || seaLevel > 255) {
            seaLevel = DEFAULT.seaLevel();
        }
        if (worldHeight < 256) {
            worldHeight = DEFAULT.worldHeight();
        }
    }

    /** 序列化为 JSON 字符串（用于哈希命名数据包 + 分享码）。 */
    public String serialize() {
        return "{\"maskFrequency\":" + maskFrequency
                + ",\"maskOctaves\":" + maskOctaves
                + ",\"bShare\":" + bShare
                + ",\"boundary\":\"" + boundary.name()
                + "\",\"seaLevel\":" + seaLevel
                + ",\"worldHeight\":" + worldHeight + "}";
    }

    /** 从分享码反序列化。 */
    public static ShanshuiSettings parse(String json) {
        ShanshuiSettings s = DEFAULT;
        try {
            float mf = s.maskFrequency();
            int mo = s.maskOctaves();
            float bs = s.bShare();
            BoundaryMode bm = s.boundary();
            int sl = s.seaLevel();
            int wh = s.worldHeight();
            for (String pair : json.replace("{", "").replace("}", "").split(",")) {
                String[] kv = pair.split(":", 2);
                if (kv.length != 2) continue;
                String k = kv[0].trim().replace("\"", "");
                String v = kv[1].trim().replace("\"", "");
                switch (k) {
                    case "maskFrequency" -> mf = Float.parseFloat(v);
                    case "maskOctaves" -> mo = Integer.parseInt(v);
                    case "bShare" -> bs = Float.parseFloat(v);
                    case "boundary" -> bm = BoundaryMode.from(v);
                    case "seaLevel" -> sl = Integer.parseInt(v);
                    case "worldHeight" -> wh = Integer.parseInt(v);
                    default -> {}
                }
            }
            return new ShanshuiSettings(mf, mo, bs, bm, sl, wh);
        } catch (Exception e) {
            return DEFAULT;
        }
    }
}
