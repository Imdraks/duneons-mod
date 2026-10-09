package dev.imdraks.duneons;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;

final class RegistryManifest {
    private RegistryManifest() {
    }

    static List<String> read(String name) {
        try (InputStream stream = RegistryManifest.class.getClassLoader().getResourceAsStream(name)) {
            if (stream == null) {
                throw new IllegalStateException("Missing registry manifest: " + name);
            }
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(stream, StandardCharsets.UTF_8))) {
                return reader.lines()
                        .map(String::trim)
                        .filter(line -> !line.isEmpty() && !line.startsWith("#"))
                        .distinct()
                        .toList();
            }
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot read registry manifest: " + name, exception);
        }
    }
}
