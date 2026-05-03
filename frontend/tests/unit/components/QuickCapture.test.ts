import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import QuickCapture from "$lib/components/QuickCapture.svelte";

describe("QuickCapture", () => {
  it("renders a textarea and a submit button", () => {
    render(QuickCapture, { props: { onCreate: vi.fn() } });
    expect(screen.getByRole("textbox")).toBeTruthy();
    expect(screen.getByRole("button", { name: /anlegen/i })).toBeTruthy();
  });

  it("calls onCreate with content and default type 'note' on button click", async () => {
    const onCreate = vi.fn();
    render(QuickCapture, { props: { onCreate } });
    const textarea = screen.getByRole("textbox");
    await fireEvent.input(textarea, { target: { value: "Mein erster Atom" } });
    await fireEvent.click(screen.getByRole("button", { name: /anlegen/i }));
    expect(onCreate).toHaveBeenCalledOnce();
    expect(onCreate).toHaveBeenCalledWith({
      content: "Mein erster Atom",
      type: "note",
    });
  });

  it("does not call onCreate when content is empty", async () => {
    const onCreate = vi.fn();
    render(QuickCapture, { props: { onCreate } });
    await fireEvent.click(screen.getByRole("button", { name: /anlegen/i }));
    expect(onCreate).not.toHaveBeenCalled();
  });

  it("clears textarea after successful onCreate call", async () => {
    const onCreate = vi.fn();
    render(QuickCapture, { props: { onCreate } });
    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement;
    await fireEvent.input(textarea, { target: { value: "test" } });
    await fireEvent.click(screen.getByRole("button", { name: /anlegen/i }));
    expect(textarea.value).toBe("");
  });

  it("calls onCreate with selected type", async () => {
    const onCreate = vi.fn();
    render(QuickCapture, { props: { onCreate } });
    const select = screen.getByRole("combobox");
    await fireEvent.change(select, { target: { value: "task" } });
    const textarea = screen.getByRole("textbox");
    await fireEvent.input(textarea, { target: { value: "Aufgabe xyz" } });
    await fireEvent.click(screen.getByRole("button", { name: /anlegen/i }));
    expect(onCreate).toHaveBeenCalledWith({ content: "Aufgabe xyz", type: "task" });
  });

  it("submits on Ctrl+Enter", async () => {
    const onCreate = vi.fn();
    render(QuickCapture, { props: { onCreate } });
    const textarea = screen.getByRole("textbox");
    await fireEvent.input(textarea, { target: { value: "keyboard shortcut" } });
    await fireEvent.keyDown(textarea, { key: "Enter", ctrlKey: true });
    expect(onCreate).toHaveBeenCalledWith({
      content: "keyboard shortcut",
      type: "note",
    });
  });
});
