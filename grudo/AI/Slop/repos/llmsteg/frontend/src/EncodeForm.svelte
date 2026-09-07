<script lang="ts">
	import { SvelteToast } from "@zerodevx/svelte-toast";
	import { prompts } from "./lib/prompts.json";
	import { adjustTextareaHeight, copyToClipboard } from "./lib/utils";
	let encodePrompt = "";
	let hiddenMessage = "";
	let encodedResponse = "";
	let encodeLoading = false;

	$: isEncodeFormValid = () => encodePrompt && hiddenMessage && !encodeLoading;

	const setRandomPrompt = () => {
		const randomIndex = Math.floor(Math.random() * prompts.length);
		encodePrompt = prompts[randomIndex];
	};

	const encodeMessage = async () => {
		encodeLoading = true;
		const response = await fetch("/encode", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: encodePrompt,
				message: hiddenMessage,
			}),
		}).finally(() => {
			encodeLoading = false;
		});

		const result = await response.json();
		encodedResponse = result.encoded_message || "Error: No response from server";
	};
</script>

<div class="form-section">
	<h2>Encode</h2>
	<form on:submit|preventDefault={encodeMessage}>
		<div class="textarea-container">
			<label for="encodePrompt">Prompt:</label>
			<textarea id="encodePrompt" bind:value={encodePrompt} placeholder="Enter prompt text" on:input={adjustTextareaHeight}
			></textarea>
			<div class="floating-buttons">
				<button
					on:click|preventDefault={() => copyToClipboard(encodePrompt, "encode prompt")}
					title="Copy"
					class:hide={encodePrompt === ""}
				>
					📋
				</button>
				<button on:click|preventDefault={() => (encodePrompt = "")} title="Reset" class:hide={encodePrompt === ""}>🔄</button>
				<button on:click|preventDefault={() => setRandomPrompt()} title="Random Prompt">🎲</button>
			</div>
		</div>

		<div class="textarea-container">
			<label for="hiddenMessage">Hidden Message:</label>
			<textarea id="hiddenMessage" bind:value={hiddenMessage} placeholder="Enter hidden message" on:input={adjustTextareaHeight}
			></textarea>
			<div class="floating-buttons" class:hide={hiddenMessage === ""}>
				<button on:click|preventDefault={() => copyToClipboard(hiddenMessage, "hidden message")} title="Copy">📋</button>
				<button on:click|preventDefault={() => (hiddenMessage = "")} title="Reset">🔄</button>
			</div>
		</div>

		<button type="submit" disabled={!isEncodeFormValid()}>
			{#if encodeLoading}
				<div class="spinner"></div>
			{:else}
				Encode
			{/if}
		</button>
	</form>

	<div class="response">
		<h3>Encoded Response:</h3>
		<p>{encodedResponse}</p>
		<div class="floating-buttons">
			<button
				on:click|preventDefault={() => copyToClipboard(encodedResponse, "encoded response")}
				title="Copy"
				class:hide={encodedResponse === ""}>📋</button
			>
		</div>
	</div>
</div>

<SvelteToast />
