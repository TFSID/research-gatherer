// npm install @heyputer/puter.js
import { puter } from '@heyputer/puter.js';

async function main() {
    try {
        // Using claude-haiku-4-5 model
        const response1 = await puter.ai.chat(
            "Write a short poem about coding",
            { model: "claude-haiku-4-5" }
        );
        console.log("=== claude-haiku-4-5 ===");
        console.log(response1.message.content[0].text);

        // Using claude-opus-4-8 model
        const response2 = await puter.ai.chat(
            "Write a short poem about coding",
            { model: "claude-opus-4-8" }
        );
        console.log("\n=== claude-opus-4-8 ===");
        console.log(response2.message.content[0].text);
    } catch (error) {
        console.error("Error:", error.message || error);
    }
}

main();
