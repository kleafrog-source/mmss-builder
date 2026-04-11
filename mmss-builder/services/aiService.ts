import { GoogleGenAI } from "@google/genai";
import { AIProvider, MMSSRoot } from "../types";
import { INITIAL_SYSTEM_PROMPT } from "../constants";

// Helper to clean markdown JSON
const cleanJsonOutput = (text: string): string => {
  let cleaned = text.trim();
  // Remove markdown code blocks if present
  if (cleaned.startsWith('```json')) {
    cleaned = cleaned.replace(/^```json/, '').replace(/```$/, '');
  } else if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```/, '').replace(/```$/, '');
  }
  return cleaned.trim();
};

export const generateMMSS = async (
  description: string,
  provider: AIProvider,
  apiKey: string
): Promise<MMSSRoot> => {
  if (!apiKey) {
    throw new Error(`API Key for ${provider} is missing.`);
  }

  const fullPrompt = INITIAL_SYSTEM_PROMPT.replace('${USER_INPUT}', description);

  try {
    let jsonString = "";

    if (provider === AIProvider.GEMINI) {
      const ai = new GoogleGenAI({ apiKey });
      
      // Using gemini-2.5-flash as the efficient default for structure generation
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: fullPrompt,
        config: {
          responseMimeType: 'application/json',
          temperature: 0.2, // Low temperature for consistent structural output
        }
      });
      
      jsonString = response.text || "{}";

    } else if (provider === AIProvider.MISTRAL) {
      // Mistral API Implementation using fetch
      const response = await fetch("https://api.mistral.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: "mistral-tiny", // or mistral-small, mistral-medium depending on user access
          messages: [
            { role: "user", content: fullPrompt }
          ],
          temperature: 0.2,
          response_format: { type: "json_object" } // Force JSON if supported by model, otherwise prompt handles it
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || `Mistral API Error: ${response.statusText}`);
      }

      const data = await response.json();
      jsonString = data.choices[0]?.message?.content || "{}";
    }

    const parsed = JSON.parse(cleanJsonOutput(jsonString));
    return parsed as MMSSRoot;

  } catch (e: any) {
    console.error("AI Generation Error:", e);
    throw new Error(e.message || "Failed to generate MMSS configuration.");
  }
};
