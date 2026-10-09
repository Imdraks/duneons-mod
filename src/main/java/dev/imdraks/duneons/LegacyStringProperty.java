package dev.imdraks.duneons;

import net.minecraft.world.level.block.state.properties.Property;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** A block-state property whose legal values are recovered from legacy data. */
final class LegacyStringProperty extends Property<String> {
    private final List<String> values;
    private final Map<String, Integer> indexes;

    LegacyStringProperty(String name, List<String> values) {
        super(name, String.class);
        if (values.size() < 2) {
            throw new IllegalArgumentException("A property requires at least two values: " + name);
        }
        this.values = List.copyOf(values);
        this.indexes = new LinkedHashMap<>();
        for (int index = 0; index < this.values.size(); index++) {
            this.indexes.put(this.values.get(index), index);
        }
    }

    @Override
    public List<String> getPossibleValues() {
        return values;
    }

    @Override
    public String getName(String value) {
        return value;
    }

    @Override
    public Optional<String> getValue(String name) {
        return indexes.containsKey(name) ? Optional.of(name) : Optional.empty();
    }

    @Override
    public int getInternalIndex(String value) {
        return indexes.getOrDefault(value, -1);
    }
}
