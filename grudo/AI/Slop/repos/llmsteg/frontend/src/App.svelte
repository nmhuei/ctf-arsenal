<script lang="ts">
	import type { SvelteToastOptions } from "@zerodevx/svelte-toast";
	import { SvelteToast, toast } from "@zerodevx/svelte-toast";
	import DecodeForm from "./DecodeForm.svelte";
	import EncodeForm from "./EncodeForm.svelte";
	import { prompts } from "./lib/prompts.json";

	const toastOptions: SvelteToastOptions = {
		theme: {
			"--toastColor": "mintcream",
			"--toastBackground": "rgba(72,187,120,0.9)",
			"--toastBarBackground": "#2F855A",
		},
	};

	let encodePrompt = "";
	let hiddenMessage = "";
	let encodedResponse = "";
	let encodeLoading = false;

	let decodePrompt = "";
	let coverMessage = "";
	let decodedResponse = "";
	let decodeLoading = false;

	$: isEncodeFormValid = () => encodePrompt && hiddenMessage && !encodeLoading;
	$: isDecodeFormValid = () => decodePrompt && coverMessage && !decodeLoading;

	const copyToClipboard = (text: string, type?: string) => {
		navigator.clipboard.writeText(text);
		toast.push(`Copied${type ? " " + type : ""} to clipboard`);
	};

	const getRandomPrompt = () => {
		const randomIndex = Math.floor(Math.random() * prompts.length);
		return prompts[randomIndex];
	};

	const setRandomPrompt = (type: "encode" | "decode") => {
		const randomPrompt = getRandomPrompt();
		if (type === "encode") {
			encodePrompt = randomPrompt;
		} else {
			decodePrompt = randomPrompt;
		}
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

	const adjustTextareaHeight = (event: Event) => {
		const textarea = event.target as HTMLTextAreaElement;
		textarea.style.height = "auto"; // Reset the height to calculate new height
		textarea.style.height = textarea.scrollHeight + "px"; // Set the height based on scroll height
	};
</script>

<svelte:head>
	<title>LLM Steganography</title>
</svelte:head>

<h1>LLM Steganography</h1>

<EncodeForm />
<DecodeForm />

<SvelteToast options={toastOptions} />
