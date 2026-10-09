package dev.imdraks.duneons;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

final class BlockStateSchemas {
    private static final String MANIFEST = "duneons/registry/block-properties.json";

    private BlockStateSchemas() {
    }

    static Map<String, List<LegacyStringProperty>> load() {
        try (InputStream stream = BlockStateSchemas.class.getClassLoader().getResourceAsStream(MANIFEST)) {
            if (stream == null) {
                throw new IllegalStateException("Missing block-state manifest: " + MANIFEST);
            }
            JsonObject root = JsonParser.parseReader(
                    new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
            Map<String, List<LegacyStringProperty>> result = new LinkedHashMap<>();
            for (Map.Entry<String, JsonElement> block : root.entrySet()) {
                List<LegacyStringProperty> properties = new ArrayList<>();
                for (Map.Entry<String, JsonElement> property : block.getValue().getAsJsonObject().entrySet()) {
                    List<String> values = new ArrayList<>();
                    property.getValue().getAsJsonArray().forEach(value -> values.add(value.getAsString()));
                    properties.add(new LegacyStringProperty(property.getKey(), values));
                }
                result.put(block.getKey(), List.copyOf(properties));
            }
            return Map.copyOf(result);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot read block-state manifest: " + MANIFEST, exception);
        }
    }
}
