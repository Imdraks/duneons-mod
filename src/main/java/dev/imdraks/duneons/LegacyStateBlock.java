package dev.imdraks.duneons;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.Property;

import java.util.List;

/**
 * Generic preservation block that retains every state property referenced by
 * the original blockstate assets and structure palettes.
 */
final class LegacyStateBlock extends Block {
    private static final ThreadLocal<List<? extends Property<?>>> CONSTRUCTION_PROPERTIES = new ThreadLocal<>();

    private LegacyStateBlock(Properties properties) {
        super(properties);
    }

    static LegacyStateBlock create(Properties properties, List<LegacyStringProperty> stateProperties) {
        CONSTRUCTION_PROPERTIES.set(stateProperties);
        try {
            return new LegacyStateBlock(properties);
        } finally {
            CONSTRUCTION_PROPERTIES.remove();
        }
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        List<? extends Property<?>> properties = CONSTRUCTION_PROPERTIES.get();
        if (properties != null && !properties.isEmpty()) {
            builder.add(properties.toArray(Property<?>[]::new));
        }
    }
}
