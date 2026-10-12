package com.shanshui;

import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ShanshuiUI implements ClientModInitializer {
    public static final String MOD_ID = "shanshui";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitializeClient() {
        LOGGER.info("Shanshui UI loaded - 超级地形调度器界面");
    }
}
