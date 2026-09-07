import { toast } from "@zerodevx/svelte-toast";

export const copyToClipboard = (text: string, type?: string) => {
	navigator.clipboard.writeText(text);
	toast.push(`Copied${type ? " " + type : ""} to clipboard`);
};

export const adjustTextareaHeight = (event: Event) => {
	const textarea = event.target as HTMLTextAreaElement;
	textarea.style.height = "auto"; // Reset the height to calculate new height
	textarea.style.height = textarea.scrollHeight + "px"; // Set the height based on scroll height
};
