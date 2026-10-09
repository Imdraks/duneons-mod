package dev.imdraks.duneons;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.level.Level;

/**
 * Compatibility entity used while the original 250 specialized entity
 * implementations are migrated.  Every original registry identifier points
 * to a real, summonable entity instead of an inert item placeholder.
 */
public final class LegacyEntity extends Zombie {
    public LegacyEntity(EntityType<? extends Zombie> type, Level level) {
        super(type, level);
    }
}
