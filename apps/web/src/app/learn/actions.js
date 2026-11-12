"use server";

import { apiPost } from "@/lib/api";

/**
 * Check one quiz answer with the API. Runs on the server.
 * @param {number} questionId
 * @param {number} optionId
 */
export async function checkAnswer(questionId, optionId) {
    return apiPost(`/learn/questions/${Number(questionId)}/check`, {
        option_id: Number(optionId),
    });
}