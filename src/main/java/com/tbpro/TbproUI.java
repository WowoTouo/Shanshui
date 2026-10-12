package com.tbpro;

import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TbproUI implements ClientModInitializer {
    public static final String MOD_ID = "tbpro";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitializeClient() {
        LOGGER.info("TBPRO UI loaded - 超级地形调度器界面");
    }
}
