<script lang="ts">
	import { adjustTextareaHeight, copyToClipboard } from "./lib/utils";
	let decodePrompt = "";
	let coverMessage = "";
	let decodedResponse = "";
	let decodeLoading = false;

	$: isDecodeFormValid = () => decodePrompt && coverMessage && !decodeLoading;

	const decodeMessage = async () => {
		decodeLoading = true;
		const response = await fetch("/decode", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: decodePrompt,
				cover_text: coverMessage,
			}),
		}).finally(() => {
			decodeLoading = false;
		});

		const result = await response.json();
		decodedResponse = result.decoded_message || "Error: No response from server";
	};
</script>

<div class="form-section">
	<h2>Decode</h2>
	<form on:submit|preventDefault={decodeMessage}>
		<div class="textarea-container">
			<label for="decodePrompt">Prompt:</label>
			<textarea id="decodePrompt" bind:value={decodePrompt} placeholder="Enter prompt text" on:input={adjustTextareaHeight}
			></textarea>
			<div class="floating-buttons">
				<button
					on:click|preventDefault={() => copyToClipboard(decodePrompt, "decode prompt")}
					title="Copy"
					class:hide={decodePrompt === ""}>📋</button
				>
				<button on:click|preventDefault={() => (decodePrompt = "")} title="Reset" class:hide={decodePrompt === ""}>🔄</button>
			</div>
		</div>

		<div class="textarea-container">
			<label for="coverMessage">Cover Message:</label>
			<textarea id="coverMessage" bind:value={coverMessage} placeholder="Enter cover message" on:input={adjustTextareaHeight}
			></textarea>
			<div class="floating-buttons" class:hide={coverMessage === ""}>
				<button on:click|preventDefault={() => copyToClipboard(coverMessage, "cover message")} title="Copy">📋</button>
				<button on:click|preventDefault={() => (coverMessage = "")} title="Reset">🔄</button>
			</div>
		</div>

		<button type="submit" disabled={!isDecodeFormValid()}>
			{#if decodeLoading}
				<div class="spinner"></div>
			{:else}
				Decode
			{/if}
		</button>
	</form>

	<div class="response">
		<h3>Decoded Response:</h3>
		<p>{decodedResponse}</p>
		<div class="floating-buttons" class:hide={decodedResponse === ""}>
			<button on:click|preventDefault={() => copyToClipboard(decodedResponse, "decoded response")} title="Copy">📋</button>
		</div>
	</div>
</div>
