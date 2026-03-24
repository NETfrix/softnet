import { writable } from "svelte/store";
import type { ProjectMeta } from "./types";

export const currentProject = writable<ProjectMeta | null>(null);
export const projects = writable<ProjectMeta[]>([]);
export const runningTasks = writable<string[]>([]);
export const statusMessage = writable<string>("");
