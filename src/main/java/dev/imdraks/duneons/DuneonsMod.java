package dev.imdraks.duneons;

import com.mojang.logging.LogUtils;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import org.slf4j.Logger;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

@Mod(DuneonsMod.MOD_ID)
public final class DuneonsMod {
    public static final String MOD_ID = "duneons";
    public static final Logger LOGGER = LogUtils.getLogger();

    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(MOD_ID);
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(MOD_ID);
    private static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(Registries.ENTITY_TYPE, MOD_ID);
    private static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MOD_ID);

    private static final List<Supplier<? extends Item>> CREATIVE_CONTENT = new ArrayList<>();
    private static final List<DeferredHolder<EntityType<?>, EntityType<LegacyEntity>>> ENTITY_TYPES =
            new ArrayList<>();
    private static final Map<String, DeferredHolder<EntityType<?>, EntityType<LegacyEntity>>> ENTITY_BY_ID =
            new LinkedHashMap<>();

    static {
        Map<String, List<LegacyStringProperty>> blockStateSchemas = BlockStateSchemas.load();

        for (String id : RegistryManifest.read("duneons/registry/entities.txt")) {
            DeferredHolder<EntityType<?>, EntityType<LegacyEntity>> entity = ENTITIES.register(id, identifier ->
                    EntityType.Builder.of(LegacyEntity::new, MobCategory.CREATURE)
                            .sized(0.6F, 1.95F)
                            .clientTrackingRange(8)
                            .build(ResourceKey.create(Registries.ENTITY_TYPE, identifier)));
            ENTITY_TYPES.add(entity);
            ENTITY_BY_ID.put(id, entity);
        }

        for (String id : RegistryManifest.read("duneons/registry/blocks.txt")) {
            List<LegacyStringProperty> stateProperties = blockStateSchemas.getOrDefault(id, List.of());
            DeferredBlock<Block> block = BLOCKS.registerBlock(id,
                    properties -> LegacyStateBlock.create(properties, stateProperties),
                    properties -> properties.mapColor(MapColor.STONE).strength(1.5F, 6.0F));
            DeferredItem<?> item = ITEMS.registerSimpleBlockItem(id, block);
            CREATIVE_CONTENT.add(item);
        }

        for (String id : RegistryManifest.read("duneons/registry/items.txt")) {
            Supplier<? extends Item> item;
            if (id.endsWith("_spawn_egg")) {
                String entityId = id.substring(0, id.length() - "_spawn_egg".length());
                DeferredHolder<EntityType<?>, EntityType<LegacyEntity>> entity = ENTITY_BY_ID.get(entityId);
                if (entity == null) {
                    throw new IllegalStateException("Spawn egg without entity registry: " + id);
                }
                item = ITEMS.registerItem(id, SpawnEggItem::new,
                        properties -> properties.spawnEgg(entity.get()));
            } else {
                item = ITEMS.registerSimpleItem(id);
            }
            CREATIVE_CONTENT.add(item);
        }
    }

    private static final DeferredHolder<CreativeModeTab, CreativeModeTab> LEGACY_CONTENT =
            TABS.register("legacy_content", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.tabdungeons"))
                    .icon(() -> CREATIVE_CONTENT.getFirst().get().getDefaultInstance())
                    .displayItems((parameters, output) ->
                            CREATIVE_CONTENT.forEach(entry -> output.accept(entry.get())))
                    .build());

    public DuneonsMod(IEventBus modBus) {
        ENTITIES.register(modBus);
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
        TABS.register(modBus);
        modBus.addListener(DuneonsMod::createEntityAttributes);
        LOGGER.info("Registering {} blocks and {} creative entries for Dungeons Content",
                RegistryManifest.read("duneons/registry/blocks.txt").size(), CREATIVE_CONTENT.size());
    }

    public static List<DeferredHolder<EntityType<?>, EntityType<LegacyEntity>>> entityTypes() {
        return List.copyOf(ENTITY_TYPES);
    }

    private static void createEntityAttributes(EntityAttributeCreationEvent event) {
        var attributes = Zombie.createAttributes().build();
        ENTITY_TYPES.forEach(type -> event.put(type.get(), attributes));
    }
}
