package dev.imdraks.duneons;

import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@EventBusSubscriber(modid = DuneonsMod.MOD_ID, value = Dist.CLIENT)
public final class DuneonsClient {
    private DuneonsClient() {
    }

    @SubscribeEvent
    @SuppressWarnings({"rawtypes", "unchecked"})
    public static void registerEntityRenderers(EntityRenderersEvent.RegisterRenderers event) {
        DuneonsMod.entityTypes().forEach(type ->
                event.registerEntityRenderer((EntityType<? extends Entity>) (EntityType) type.get(),
                        context -> (net.minecraft.client.renderer.entity.EntityRenderer) new ZombieRenderer(context)));
    }
}
