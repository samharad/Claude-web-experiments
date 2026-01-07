#!/usr/bin/env python3
"""
Stop Motion Video Maker - Python GUI Tool
Requires: Python 3, Pillow, ffmpeg (command-line)
Install dependencies: pip install Pillow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import tempfile
import shutil
from pathlib import Path


class Frame:
    def __init__(self, path, duration=500):
        self.path = path
        self.duration = duration
        self.thumbnail = None


class StopMotionMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Stop Motion Video Maker")
        self.root.geometry("1000x700")

        self.frames = []
        self.thumbnails = {}

        self.setup_ui()

    def setup_ui(self):
        # Top controls
        controls_frame = ttk.Frame(self.root, padding="10")
        controls_frame.pack(fill=tk.X)

        ttk.Button(controls_frame, text="Add Images", command=self.add_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        ttk.Label(controls_frame, text="Default Duration (ms):").pack(side=tk.LEFT, padx=(20, 5))
        self.default_duration = tk.IntVar(value=500)
        ttk.Spinbox(controls_frame, from_=1, to=10000, textvariable=self.default_duration, width=10).pack(side=tk.LEFT)

        ttk.Label(controls_frame, text="Output FPS:").pack(side=tk.LEFT, padx=(20, 5))
        self.fps = tk.IntVar(value=10)
        ttk.Spinbox(controls_frame, from_=1, to=60, textvariable=self.fps, width=10).pack(side=tk.LEFT)

        ttk.Button(controls_frame, text="Generate MP4", command=self.generate_video, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

        # Main area with frames list and controls
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - frame list with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(list_frame, text="Frames:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))

        # Scrollable canvas for frames
        canvas_frame = ttk.Frame(list_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, padding="5")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )

        if files:
            for file in files:
                frame = Frame(file, self.default_duration.get())
                self.frames.append(frame)

            self.render_frames()
            self.status_var.set(f"Added {len(files)} images. Total frames: {len(self.frames)}")

    def clear_all(self):
        if self.frames and messagebox.askyesno("Clear All", "Remove all frames?"):
            self.frames = []
            self.thumbnails = {}
            self.render_frames()
            self.status_var.set("All frames cleared")

    def render_frames(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.frames:
            ttk.Label(self.scrollable_frame, text="No frames yet. Click 'Add Images' to get started.",
                     foreground='gray').pack(pady=50)
            return

        for idx, frame in enumerate(self.frames):
            self.render_frame_item(idx, frame)

    def render_frame_item(self, idx, frame):
        # Container for each frame
        frame_container = ttk.Frame(self.scrollable_frame, relief=tk.RIDGE, borderwidth=2)
        frame_container.pack(fill=tk.X, padx=5, pady=5)

        # Left side - thumbnail and info
        left_frame = ttk.Frame(frame_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame number
        ttk.Label(left_frame, text=f"#{idx + 1}", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=(0, 10))

        # Thumbnail
        if frame.path not in self.thumbnails:
            try:
                img = Image.open(frame.path)
                img.thumbnail((80, 80))
                photo = ImageTk.PhotoImage(img)
                self.thumbnails[frame.path] = photo
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
                self.thumbnails[frame.path] = None

        if self.thumbnails[frame.path]:
            ttk.Label(left_frame, image=self.thumbnails[frame.path]).pack(side=tk.LEFT, padx=(0, 10))

        # Info
        info_frame = ttk.Frame(left_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(info_frame, text=Path(frame.path).name, font=('Arial', 9)).pack(anchor=tk.W)

        duration_frame = ttk.Frame(info_frame)
        duration_frame.pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(duration_frame, text="Duration:").pack(side=tk.LEFT)

        duration_var = tk.IntVar(value=frame.duration)
        duration_spin = ttk.Spinbox(duration_frame, from_=1, to=10000, textvariable=duration_var, width=10)
        duration_spin.pack(side=tk.LEFT, padx=5)

        # Update duration on change
        def update_duration(f=frame, var=duration_var):
            f.duration = var.get()

        duration_spin.configure(command=update_duration)
        duration_var.trace_add('write', lambda *args, f=frame, var=duration_var: setattr(f, 'duration', var.get()))

        ttk.Label(duration_frame, text="ms").pack(side=tk.LEFT)

        # Right side - controls
        controls_frame = ttk.Frame(frame_container)
        controls_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        button_frame = ttk.Frame(controls_frame)
        button_frame.pack()

        if idx > 0:
            ttk.Button(button_frame, text="↑", width=3, command=lambda i=idx: self.move_up(i)).pack(side=tk.LEFT, padx=2)

        if idx < len(self.frames) - 1:
            ttk.Button(button_frame, text="↓", width=3, command=lambda i=idx: self.move_down(i)).pack(side=tk.LEFT, padx=2)

        ttk.Button(button_frame, text="✕", width=3, command=lambda i=idx: self.delete_frame(i)).pack(side=tk.LEFT, padx=2)

    def move_up(self, idx):
        if idx > 0:
            self.frames[idx], self.frames[idx - 1] = self.frames[idx - 1], self.frames[idx]
            self.render_frames()

    def move_down(self, idx):
        if idx < len(self.frames) - 1:
            self.frames[idx], self.frames[idx + 1] = self.frames[idx + 1], self.frames[idx]
            self.render_frames()

    def delete_frame(self, idx):
        del self.frames[idx]
        self.render_frames()
        self.status_var.set(f"Frame deleted. Total frames: {len(self.frames)}")

    def generate_video(self):
        if not self.frames:
            messagebox.showwarning("No Frames", "Please add some frames first!")
            return

        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("FFmpeg Not Found",
                               "FFmpeg is not installed or not in PATH.\n\n"
                               "Please install FFmpeg:\n"
                               "- macOS: brew install ffmpeg\n"
                               "- Linux: sudo apt install ffmpeg\n"
                               "- Windows: Download from ffmpeg.org")
            return

        # Ask for output file
        output_file = filedialog.asksaveasfilename(
            title="Save Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4"), ("All files", "*.*")]
        )

        if not output_file:
            return

        self.status_var.set("Generating video...")
        self.root.update()

        try:
            self._generate_video_internal(output_file)
            self.status_var.set(f"Video saved to {output_file}")
            messagebox.showinfo("Success", f"Video generated successfully!\n\n{output_file}")
        except Exception as e:
            self.status_var.set("Error generating video")
            messagebox.showerror("Error", f"Failed to generate video:\n\n{str(e)}")

    def _generate_video_internal(self, output_file):
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Copy and rename images to temp directory
            concat_content = ""

            for idx, frame in enumerate(self.frames):
                # Copy image to temp dir with padded name
                temp_image = os.path.join(temp_dir, f"frame{idx:04d}.png")

                # Convert to PNG if needed
                img = Image.open(frame.path)
                img.save(temp_image, 'PNG')

                # Add to concat file
                duration_seconds = frame.duration / 1000.0
                concat_content += f"file 'frame{idx:04d}.png'\n"
                concat_content += f"duration {duration_seconds}\n"

            # Add last frame again (ffmpeg concat demuxer requirement)
            concat_content += f"file 'frame{len(self.frames) - 1:04d}.png'\n"

            # Write concat file
            concat_file = os.path.join(temp_dir, 'concat.txt')
            with open(concat_file, 'w') as f:
                f.write(concat_content)

            # Run ffmpeg
            fps = self.fps.get()
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-vf', f'fps={fps}',
                '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264',
                output_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir)

            if result.returncode != 0:
                raise Exception(f"FFmpeg error:\n{result.stderr}")

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    root = tk.Tk()

    # Set up theme
    style = ttk.Style()
    style.theme_use('default')

    app = StopMotionMaker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
