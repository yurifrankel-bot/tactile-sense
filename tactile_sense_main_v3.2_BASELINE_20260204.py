#!/usr/bin/env python3
"""
TactileSense v3.2 - Digital Master Record (DMR) Edition
With LIVE visual feedback while adjusting pressure zones

NEW in v3.1:
- Interactive sliders for zone boundaries
- Live preview showing sample fingers at different pressures
- See colors change in REAL-TIME as you drag sliders
- Visual zone boundary bar
- Quick presets for common PT techniques
- Much easier to configure zones!

All v3.0 features included:
- PT-defined pressure zones (Blue/Green/Yellow/Red)
- 3D hand orientation display
- Visual hand with color-coded fingers
- Demo simulator and TactileGlove modes
"""

import sys
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import json  # NEW in v3.2 for DMR file save/load
import os    # file-system helpers: mkdir, path joining
import csv   # CSV writer for export

print("Starting TactileSense v3.2 - Digital Master Record (DMR) Edition...")


# ============================================================================
# DIGITAL MASTER RECORD (DMR) COMPONENTS - NEW IN v3.2
# ============================================================================

class DMRSessionDialog:
    """
    Digital Master Record session metadata capture dialog.
    Collects patient ID, PT/PTA IDs, treatment location, and session notes.
    """
    
    def __init__(self, parent, callback):
        """
        Args:
            parent: TactileSenseClinical instance (not root window)
            callback: Function to call with session metadata
        """
        self.parent = parent  # TactileSenseClinical instance
        self.callback = callback
        self.result = None
        
        # Create dialog window using parent's root
        root_window = parent.root if hasattr(parent, 'root') else parent
        self.dialog = tk.Toplevel(root_window)
        self.dialog.title("📋 Digital Master Record - New Session")
        self.dialog.geometry("650x750")  # Back to 750 since auto-export section removed
        self.dialog.transient(root_window)
        self.dialog.grab_set()
        
        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (750 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_ui()
    
    def _create_ui(self):
        """Create DMR session metadata form"""
        # Header
        header = ttk.Frame(self.dialog)
        header.pack(fill=tk.X, pady=15, padx=20)
        
        ttk.Label(header, text="Digital Master Record (DMR)",
                 font=('Arial', 18, 'bold')).pack()
        ttk.Label(header, text="Enter session information before recording",
                 font=('Arial', 10), foreground="blue").pack(pady=(5,0))
        
        # Scrollable main area
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20,0))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,20))
        
        # Auto-captured information
        auto_frame = ttk.LabelFrame(scrollable_frame, text="📅 Auto-Captured", padding=15)
        auto_frame.pack(fill=tk.X, pady=(10,15), padx=10)
        
        now = datetime.now()
        self.session_id = f"DMR-{now.strftime('%Y%m%d-%H%M%S')}"
        
        info_grid = ttk.Frame(auto_frame)
        info_grid.pack()
        
        ttk.Label(info_grid, text="Session ID:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=3, padx=(0,10))
        ttk.Label(info_grid, text=self.session_id, font=('Arial', 9),
                 foreground="darkblue").grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_grid, text="Date:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=3, padx=(0,10))
        ttk.Label(info_grid, text=now.strftime("%Y-%m-%d"), font=('Arial', 9),
                 foreground="darkblue").grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(info_grid, text="Time:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=3, padx=(0,10))
        ttk.Label(info_grid, text=now.strftime("%H:%M:%S"), font=('Arial', 9),
                 foreground="darkblue").grid(row=2, column=1, sticky=tk.W)
        
        # Patient information
        patient_frame = ttk.LabelFrame(scrollable_frame, text="👤 Patient Information *", padding=15)
        patient_frame.pack(fill=tk.X, pady=(0,15), padx=10)
        
        ttk.Label(patient_frame, text="Patient ID:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))
        self.entry_patient_id = ttk.Entry(patient_frame, width=30, font=('Arial', 11))
        self.entry_patient_id.pack(fill=tk.X, pady=(0,5))
        ttk.Label(patient_frame, text="Enter patient identification number or code",
                 font=('Arial', 8), foreground="gray").pack(anchor=tk.W)
        
        # Treatment location
        location_frame = ttk.LabelFrame(scrollable_frame, text="📍 Treatment Location *", padding=15)
        location_frame.pack(fill=tk.X, pady=(0,15), padx=10)
        
        ttk.Label(location_frame, text="Select body part being treated:",
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0,10))
        
        self.location_var = tk.StringVar(value="")
        
        locations = [
            ("Left Shoulder", "left_shoulder"),
            ("Right Shoulder", "right_shoulder"),
            ("Lower Back", "lower_back"),
            ("Left Knee", "left_knee"),
            ("Right Knee", "right_knee"),
            ("Left Ankle", "left_ankle"),
            ("Right Ankle", "right_ankle")
        ]
        
        loc_container = ttk.Frame(location_frame)
        loc_container.pack(fill=tk.X)
        
        left_locs = ttk.Frame(loc_container)
        left_locs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,15))
        
        right_locs = ttk.Frame(loc_container)
        right_locs.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        for i, (label, value) in enumerate(locations):
            parent_frame = left_locs if i < 4 else right_locs
            ttk.Radiobutton(parent_frame, text=label, variable=self.location_var,
                          value=value).pack(anchor=tk.W, pady=2)
        
        # Practitioner information
        pract_frame = ttk.LabelFrame(scrollable_frame, text="👨‍⚕️ Practitioner Information *", padding=15)
        pract_frame.pack(fill=tk.X, pady=(0,15), padx=10)
        
        ttk.Label(pract_frame, text="Physical Therapist (PT) ID:",
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))
        self.entry_pt_id = ttk.Entry(pract_frame, width=30, font=('Arial', 11))
        self.entry_pt_id.pack(fill=tk.X, pady=(0,5))
        ttk.Label(pract_frame, text="Licensed PT creating or supervising protocol",
                 font=('Arial', 8), foreground="gray").pack(anchor=tk.W, pady=(0,10))
        
        ttk.Label(pract_frame, text="Physical Therapist Assistant (PTA) ID:",
                 font=('Arial', 10)).pack(anchor=tk.W, pady=(0,5))
        self.entry_pta_id = ttk.Entry(pract_frame, width=30, font=('Arial', 11))
        self.entry_pta_id.pack(fill=tk.X, pady=(0,5))
        ttk.Label(pract_frame, text="Optional - PTA executing under supervision",
                 font=('Arial', 8), foreground="gray").pack(anchor=tk.W)
        
        # Treatment type
        type_frame = ttk.LabelFrame(scrollable_frame, text="🔬 Treatment Type *", padding=15)
        type_frame.pack(fill=tk.X, pady=(0,15), padx=10)
        
        self.treatment_type_var = tk.StringVar(value="pt_protocol")
        
        ttk.Radiobutton(type_frame,
                       text="PT Protocol Development (Creating new DMR)",
                       variable=self.treatment_type_var,
                       value="pt_protocol").pack(anchor=tk.W, pady=3)
        
        ttk.Radiobutton(type_frame,
                       text="PTA Execution (Following PT DMR)",
                       variable=self.treatment_type_var,
                       value="pta_execution").pack(anchor=tk.W, pady=3)
        
        ttk.Radiobutton(type_frame,
                       text="Robot Execution (Autonomous from DMR)",
                       variable=self.treatment_type_var,
                       value="robot_execution").pack(anchor=tk.W, pady=3)
        
        # Session notes
        notes_frame = ttk.LabelFrame(scrollable_frame, text="📝 Session Notes (Optional)", padding=15)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0,15), padx=10)
        
        ttk.Label(notes_frame, text="Clinical notes or observations:",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0,5))
        self.text_notes = tk.Text(notes_frame, height=4, width=50, font=('Arial', 9), wrap=tk.WORD)
        self.text_notes.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="✓ Start DMR Session",
                  command=self.validate_and_start, width=22).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✗ Cancel",
                  command=self.cancel, width=15).pack(side=tk.LEFT, padx=5)
        
        note_frame = ttk.Frame(self.dialog)
        note_frame.pack(pady=(0,10))
        ttk.Label(note_frame, text="* = Required field",
                 font=('Arial', 8), foreground="red").pack()
        
        self.entry_patient_id.focus()
    
    def validate_and_start(self):
        """Validate form and create session metadata"""
        patient_id = self.entry_patient_id.get().strip()
        location = self.location_var.get()
        pt_id = self.entry_pt_id.get().strip()
        pta_id = self.entry_pta_id.get().strip()
        treatment_type = self.treatment_type_var.get()
        notes = self.text_notes.get("1.0", tk.END).strip()
        
        # Validate required fields
        errors = []
        if not patient_id:
            errors.append("• Patient ID is required")
        if not location:
            errors.append("• Treatment location must be selected")
        if not pt_id:
            errors.append("• PT ID is required")
        
        if errors:
            messagebox.showerror("Missing Required Information",
                                "Please complete:\n\n" + "\n".join(errors))
            return
        
        # Location names
        location_names = {
            'left_shoulder': 'Left Shoulder',
            'right_shoulder': 'Right Shoulder',
            'lower_back': 'Lower Back',
            'left_knee': 'Left Knee',
            'right_knee': 'Right Knee',
            'left_ankle': 'Left Ankle',
            'right_ankle': 'Right Ankle'
        }
        
        treatment_names = {
            'pt_protocol': 'PT Protocol Development',
            'pta_execution': 'PTA Execution',
            'robot_execution': 'Robot Execution'
        }
        
        now = datetime.now()
        
        # Create complete session metadata
        self.result = {
            'session_id': self.session_id,
            'timestamp': now.isoformat(),
            'date': now.strftime("%Y-%m-%d"),
            'time': now.strftime("%H:%M:%S"),
            'patient_id': patient_id,
            'treatment_location': location,
            'treatment_location_display': location_names.get(location, location),
            'pt_id': pt_id,
            'pta_id': pta_id if pta_id else None,
            'treatment_type': treatment_type,
            'treatment_type_display': treatment_names.get(treatment_type, treatment_type),
            'notes': notes if notes else None,
            'auto_export_csv': self.parent.auto_export_csv_var.get(),  # Read from main UI checkbox
            'software_version': 'TactileSense v3.2 DMR Edition',
            'device': 'PT Robotic Therapeutic System',
            'dmr_version': '1.0'
        }
        
        self.callback(self.result)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel session creation"""
        self.result = None
        self.dialog.destroy()


class DMRSessionInfo(ttk.Frame):
    """Widget displaying current DMR session information"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.session_metadata = None
        self._create_ui()
    
    def _create_ui(self):
        """Create session info display"""
        self.info_label = ttk.Label(
            self,
            text="No active DMR session - Click ⏺ Record to start",
            font=('Arial', 9),
            foreground="gray"
        )
        self.info_label.pack(fill=tk.X, padx=5, pady=3)
    
    def set_session(self, metadata):
        """Update display with session metadata"""
        self.session_metadata = metadata
        
        if metadata:
            info_parts = [
                f"📋 {metadata['session_id']}",
                f"Patient: {metadata['patient_id']}",
                f"Location: {metadata['treatment_location_display']}",
                f"PT: {metadata['pt_id']}"
            ]
            
            if metadata.get('pta_id'):
                info_parts.append(f"PTA: {metadata['pta_id']}")
            
            info_text = " | ".join(info_parts)
            self.info_label.config(text=info_text, foreground="darkgreen")
        else:
            self.info_label.config(
                text="No active DMR session - Click ⏺ Record to start",
                foreground="gray"
            )
    
    def clear_session(self):
        """Clear session display"""
        self.set_session(None)



# ============================================================================
# FRAME VIEWER - Clinical Review Tool for examining recorded frames
# ============================================================================

class FrameViewer:
    """
    Frame-by-frame viewer for clinical review of recorded DMR sessions.
    Allows PTs to examine each frame visually with heatmap, stats, and navigation.
    """
    
    def __init__(self, parent, frames, pressure_zones, session_metadata=None):
        self.parent = parent
        self.frames = frames
        self.pressure_zones = pressure_zones
        self.session_metadata = session_metadata
        self.current_frame_idx = 0
        self.is_playing = False
        self.play_speed = 100  # ms per frame
        
        self.viewer = tk.Toplevel(parent)
        self.viewer.title("📊 Frame Viewer - Clinical Review")
        self.viewer.geometry("900x800")
        self.viewer.transient(parent)
        
        # Center on screen
        self.viewer.update_idletasks()
        x = (self.viewer.winfo_screenwidth() // 2) - 450
        y = (self.viewer.winfo_screenheight() // 2) - 400
        self.viewer.geometry(f"+{x}+{y}")
        
        self._create_ui()
        self._display_frame(0)
    
    def _create_ui(self):
        """Create the frame viewer UI"""
        # Header with session info
        header = ttk.Frame(self.viewer)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="Frame Viewer - Clinical Review",
                 font=('Arial', 16, 'bold')).pack()
        
        if self.session_metadata:
            info_text = (f"Session: {self.session_metadata.get('session_id', 'N/A')} | "
                        f"Patient: {self.session_metadata.get('patient_id', 'N/A')} | "
                        f"Location: {self.session_metadata.get('treatment_location_display', 'N/A')}")
            ttk.Label(header, text=info_text, font=('Arial', 9),
                     foreground="darkblue").pack(pady=(5,0))
        
        ttk.Label(header, text=f"Total Frames: {len(self.frames)}",
                 font=('Arial', 10, 'bold')).pack(pady=(5,0))
        
        ttk.Separator(self.viewer, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)
        
        # Main content area
        main = ttk.Frame(self.viewer)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Heatmap
        left = ttk.LabelFrame(main, text="🔥 Pressure Heatmap", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.heat_fig = Figure(figsize=(6, 7), dpi=90)
        self.heat_ax = self.heat_fig.add_subplot(111)
        self.heat_canvas = FigureCanvasTkAgg(self.heat_fig, left)
        self.heat_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right: Frame info and stats
        right = ttk.Frame(main, width=250)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5,0))
        right.pack_propagate(False)
        
        # Frame metadata
        meta_frame = ttk.LabelFrame(right, text="📋 Frame Info", padding=10)
        meta_frame.pack(fill=tk.X, pady=(0,10))
        
        info_grid = ttk.Frame(meta_frame)
        info_grid.pack(fill=tk.X)
        
        ttk.Label(info_grid, text="Frame:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_frame_num = ttk.Label(info_grid, text="0 / 0",
                                       font=('Arial', 9))
        self.lbl_frame_num.grid(row=0, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(info_grid, text="Time:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_timestamp = ttk.Label(info_grid, text="--:--:--",
                                       font=('Arial', 9))
        self.lbl_timestamp.grid(row=1, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(info_grid, text="Pattern:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_pattern = ttk.Label(info_grid, text="N/A",
                                     font=('Arial', 9))
        self.lbl_pattern.grid(row=2, column=1, sticky=tk.W, padx=(5,0))
        
        # Statistics
        stats_frame = ttk.LabelFrame(right, text="📊 Pressure Stats", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0,10))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        ttk.Label(stats_grid, text="Peak:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=3)
        self.lbl_peak = ttk.Label(stats_grid, text="0.0 kPa",
                                  font=('Arial', 10, 'bold'))
        self.lbl_peak.grid(row=0, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(stats_grid, text="Average:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=3)
        self.lbl_avg = ttk.Label(stats_grid, text="0.0 kPa",
                                font=('Arial', 9))
        self.lbl_avg.grid(row=1, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(stats_grid, text="Zone:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=3)
        self.lbl_zone = ttk.Label(stats_grid, text="N/A",
                                  font=('Arial', 9, 'bold'))
        self.lbl_zone.grid(row=2, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Separator(stats_grid, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(stats_grid, text="Active:", font=('Arial', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=3)
        self.lbl_active = ttk.Label(stats_grid, text="0 / 65",
                                    font=('Arial', 9))
        self.lbl_active.grid(row=4, column=1, sticky=tk.W, padx=(5,0))
        
        # Orientation (if available)
        orient_frame = ttk.LabelFrame(right, text="🔄 Orientation", padding=10)
        orient_frame.pack(fill=tk.X, pady=(0,10))
        
        orient_grid = ttk.Frame(orient_frame)
        orient_grid.pack(fill=tk.X)
        
        ttk.Label(orient_grid, text="Roll:", font=('Arial', 8)).grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_roll = ttk.Label(orient_grid, text="0°",
                                  font=('Arial', 8, 'bold'))
        self.lbl_roll.grid(row=0, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(orient_grid, text="Pitch:", font=('Arial', 8)).grid(
            row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_pitch = ttk.Label(orient_grid, text="0°",
                                   font=('Arial', 8, 'bold'))
        self.lbl_pitch.grid(row=1, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(orient_grid, text="Yaw:", font=('Arial', 8)).grid(
            row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_yaw = ttk.Label(orient_grid, text="0°",
                                font=('Arial', 8, 'bold'))
        self.lbl_yaw.grid(row=2, column=1, sticky=tk.W, padx=(5,0))
        
        # Zone reference
        zones_frame = ttk.LabelFrame(right, text="📊 Zone Ranges", padding=8)
        zones_frame.pack(fill=tk.X)
        
        zones_info = [
            ("🔵 Therapeutic Min:", f"{self.pressure_zones['therapeutic_min']:.0f} kPa"),
            ("🟢 Therapeutic Max:", f"{self.pressure_zones['therapeutic_max']:.0f} kPa"),
            ("🔴 Caution Max:", f"{self.pressure_zones['caution_max']:.0f} kPa")
        ]
        
        for label, value in zones_info:
            row = ttk.Frame(zones_frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=label, font=('Arial', 8)).pack(side=tk.LEFT)
            ttk.Label(row, text=value, font=('Arial', 8, 'bold')).pack(side=tk.RIGHT)
        
        # Navigation controls
        ttk.Separator(self.viewer, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)
        
        nav_frame = ttk.Frame(self.viewer)
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Playback controls
        playback_frame = ttk.Frame(nav_frame)
        playback_frame.pack(fill=tk.X, pady=(0,10))
        
        ttk.Label(playback_frame, text="Playback:", font=('Arial', 9, 'bold')).pack(
            side=tk.LEFT, padx=(0,10))
        
        self.btn_play = ttk.Button(playback_frame, text="▶ Play",
                                   command=self.toggle_playback, width=10)
        self.btn_play.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(playback_frame, text="Speed:", font=('Arial', 8)).pack(
            side=tk.LEFT, padx=(15,5))
        
        speed_frame = ttk.Frame(playback_frame)
        speed_frame.pack(side=tk.LEFT)
        
        ttk.Radiobutton(speed_frame, text="0.5x", value=200,
                       variable=tk.IntVar(value=self.play_speed),
                       command=lambda: setattr(self, 'play_speed', 200)).pack(
            side=tk.LEFT, padx=2)
        ttk.Radiobutton(speed_frame, text="1x", value=100,
                       variable=tk.IntVar(value=self.play_speed),
                       command=lambda: setattr(self, 'play_speed', 100)).pack(
            side=tk.LEFT, padx=2)
        ttk.Radiobutton(speed_frame, text="2x", value=50,
                       variable=tk.IntVar(value=self.play_speed),
                       command=lambda: setattr(self, 'play_speed', 50)).pack(
            side=tk.LEFT, padx=2)
        
        # Frame slider
        slider_frame = ttk.Frame(nav_frame)
        slider_frame.pack(fill=tk.X, pady=(0,10))
        
        self.frame_slider = ttk.Scale(slider_frame, from_=0,
                                      to=len(self.frames)-1,
                                      orient=tk.HORIZONTAL,
                                      command=self._on_slider_change)
        self.frame_slider.pack(fill=tk.X)
        
        # Navigation buttons
        btn_frame = ttk.Frame(nav_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="⏮ First", command=self.first_frame,
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="◀ Prev", command=self.prev_frame,
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Next ▶", command=self.next_frame,
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Last ⏭", command=self.last_frame,
                  width=10).pack(side=tk.LEFT, padx=2)
        
        # Close button
        ttk.Button(nav_frame, text="✓ Close Viewer",
                  command=self.viewer.destroy, width=20).pack(pady=(10,0))
    
    def _display_frame(self, idx):
        """Display a specific frame"""
        if idx < 0 or idx >= len(self.frames):
            print(f"✗ Frame index {idx} out of range (have {len(self.frames)} frames)")
            return
        
        self.current_frame_idx = idx
        frame = self.frames[idx]
        
        # Debug output
        if idx == 0:  # Only for first frame to avoid spam
            print(f"\n=== FRAME VIEWER DISPLAY DEBUG ===")
            print(f"Frame {idx} keys: {frame.keys()}")
            print(f"sensor_data type: {type(frame.get('sensor_data'))}")
            if frame.get('sensor_data'):
                sensor_data_sample = frame.get('sensor_data')
                print(f"sensor_data length: {len(sensor_data_sample)}")
                print(f"sensor_data first 5 values: {sensor_data_sample[:5]}")
                print(f"sensor_data data types: {[type(x) for x in sensor_data_sample[:5]]}")
        
        # Update metadata
        self.lbl_frame_num.config(text=f"{idx + 1} / {len(self.frames)}")
        
        timestamp = frame.get('timestamp', 'N/A')
        if timestamp != 'N/A' and 'T' in timestamp:
            # Extract just the time portion
            time_part = timestamp.split('T')[1].split('.')[0]
            self.lbl_timestamp.config(text=time_part)
        else:
            self.lbl_timestamp.config(text=timestamp)
        
        pattern = frame.get('demo_pattern', 'N/A')
        if pattern and pattern != 'N/A':
            # Convert pattern key to readable name
            pattern_names = {
                "idle": "No Activity",
                "ball_grip": "Ball Grip",
                "precision_pinch": "Precision Pinch",
                "power_grip": "Power Grip",
                "pt_shoulder": "PT: Shoulder",
                "pt_elbow": "PT: Elbow",
                "pt_wrist": "PT: Wrist",
                "three_finger": "Three-Finger",
                "lateral_pinch": "Lateral Pinch"
            }
            self.lbl_pattern.config(text=pattern_names.get(pattern, pattern))
        else:
            self.lbl_pattern.config(text="N/A")
        
        # Get sensor data
        sensor_data = np.array(frame.get('sensor_data', [0]*65))
        
        # Update statistics
        active = sensor_data > 1.0
        if np.any(active):
            peak = np.max(sensor_data)
            avg = np.mean(sensor_data[active])
            n_active = np.sum(active)
            
            # Determine zone
            if avg < self.pressure_zones['therapeutic_min']:
                zone = "Below Therapeutic"
                zone_color = "blue"
            elif avg <= self.pressure_zones['therapeutic_max']:
                zone = "Therapeutic ✓"
                zone_color = "green"
            elif avg <= self.pressure_zones['caution_max']:
                zone = "Above Therapeutic"
                zone_color = "orange"
            else:
                zone = "CAUTION"
                zone_color = "red"
        else:
            peak = avg = 0
            n_active = 0
            zone = "No Data"
            zone_color = "gray"
        
        self.lbl_peak.config(text=f"{peak:.1f} kPa")
        self.lbl_avg.config(text=f"{avg:.1f} kPa")
        self.lbl_zone.config(text=zone, foreground=zone_color)
        self.lbl_active.config(text=f"{int(n_active)} / 65")
        
        # Update orientation
        orientation = frame.get('hand_orientation', {})
        self.lbl_roll.config(text=f"{orientation.get('roll', 0):.1f}°")
        self.lbl_pitch.config(text=f"{orientation.get('pitch', 0):.1f}°")
        self.lbl_yaw.config(text=f"{orientation.get('yaw', 0):.1f}°")
        
        # Update heatmap
        self._draw_heatmap(sensor_data)
        
        # Update slider position
        self.frame_slider.set(idx)
    
    def _draw_heatmap(self, sensor_data):
        """Draw the pressure heatmap"""
        self.heat_ax.clear()
        
        grid = sensor_data.reshape((13, 5))
        
        im = self.heat_ax.imshow(grid, cmap='hot', interpolation='bilinear',
                                vmin=0, vmax=80, aspect='auto')
        
        self.heat_ax.set_title('Pressure Distribution (kPa)',
                              fontsize=11, fontweight='bold')
        self.heat_ax.set_xlabel('Finger', fontsize=9)
        self.heat_ax.set_ylabel('Sensor Row', fontsize=9)
        
        labels = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        self.heat_ax.set_xticks(range(5))
        self.heat_ax.set_xticklabels(labels, fontsize=8)
        self.heat_ax.tick_params(axis='y', labelsize=8)
        
        # Add colorbar if not exists
        if not hasattr(self, 'colorbar'):
            self.colorbar = self.heat_fig.colorbar(im, ax=self.heat_ax)
            self.colorbar.set_label('kPa', rotation=0, labelpad=10, fontsize=9)
            self.colorbar.ax.tick_params(labelsize=8)
        
        self.heat_canvas.draw()
    
    def _on_slider_change(self, value):
        """Handle slider movement"""
        idx = int(float(value))
        self._display_frame(idx)
    
    def first_frame(self):
        """Jump to first frame"""
        self._display_frame(0)
    
    def last_frame(self):
        """Jump to last frame"""
        self._display_frame(len(self.frames) - 1)
    
    def prev_frame(self):
        """Go to previous frame"""
        if self.current_frame_idx > 0:
            self._display_frame(self.current_frame_idx - 1)
    
    def next_frame(self):
        """Go to next frame"""
        if self.current_frame_idx < len(self.frames) - 1:
            self._display_frame(self.current_frame_idx + 1)
    
    def toggle_playback(self):
        """Toggle playback animation"""
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="▶ Play")
        else:
            self.is_playing = True
            self.btn_play.config(text="⏸ Pause")
            self._play_next()
    
    def _play_next(self):
        """Play next frame in sequence"""
        if not self.is_playing:
            return
        
        if self.current_frame_idx < len(self.frames) - 1:
            self.next_frame()
            self.viewer.after(self.play_speed, self._play_next)
        else:
            # Reached end, stop playing
            self.is_playing = False
            self.btn_play.config(text="▶ Play")


# ============================================================================
# INTERACTIVE ZONE CONFIGURATION DIALOG - FROM v3.1
# ============================================================================

class InteractiveZoneDialog:
    """Interactive dialog for configuring pressure zones with LIVE visual feedback"""
    
    def __init__(self, parent, current_zones, callback):
        self.parent = parent
        self.current_zones = current_zones.copy()
        self.callback = callback
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Configure PT Pressure Zones - Interactive")
        self.dialog.geometry("950x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Temporary zones for live preview
        self.temp_zones = current_zones.copy()
        
        self._create_ui()
        self._update_preview()
    
    def _create_ui(self):
        """Create interactive UI with sliders and live preview"""
        # Title
        title_frame = ttk.Frame(self.dialog)
        title_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(title_frame, text="Configure PT Pressure Zones",
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Drag sliders to adjust - watch colors change in real-time!",
                 font=('Arial', 10), foreground="blue").pack()
        
        # Main container with two sides
        main = ttk.Frame(self.dialog)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Left side - Sliders and controls
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        
        # Right side - Live preview
        right = ttk.LabelFrame(main, text="👁 LIVE PREVIEW", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._create_sliders(left)
        self._create_preview(right)
        
        # Bottom buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="✓ Save & Apply", command=self.save_zones,
                  width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✗ Cancel", command=self.dialog.destroy,
                  width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="↺ Reset to Default (20-45-60)", command=self.reset_default,
                  width=25).pack(side=tk.LEFT, padx=5)
    
    def _create_sliders(self, parent):
        """Create slider controls with live feedback"""
        # Instructions
        info = ttk.Label(parent, 
                        text="Drag sliders below to adjust zone boundaries.\n"
                             "Watch the preview update immediately!",
                        font=('Arial', 9), foreground="navy", justify=tk.LEFT)
        info.pack(pady=(0,10), anchor=tk.W)
        
        # ===== SLIDER 1: Therapeutic Minimum (Blue → Green boundary) =====
        frame1 = ttk.LabelFrame(parent, text="🔵 → 🟢  Therapeutic MINIMUM", padding=12)
        frame1.pack(fill=tk.X, pady=8)
        
        desc1 = ttk.Label(frame1, 
                         text="Pressure below this value = BLUE (ineffective, too low)\n"
                              "Pressure above this value = enters GREEN zone (therapeutic)",
                         font=('Arial', 8), foreground="gray", justify=tk.LEFT)
        desc1.pack(anchor=tk.W, pady=(0,5))
        
        self.var_min = tk.DoubleVar(value=self.current_zones['therapeutic_min'])
        
        slider_frame1 = ttk.Frame(frame1)
        slider_frame1.pack(fill=tk.X, pady=5)
        
        self.lbl_min = ttk.Label(slider_frame1, text=f"{self.var_min.get():.1f} kPa",
                                font=('Arial', 14, 'bold'), foreground="blue", width=12)
        self.lbl_min.pack(side=tk.LEFT, padx=(0,10))
        
        scale1 = ttk.Scale(slider_frame1, from_=5, to=50, orient=tk.HORIZONTAL,
                          variable=self.var_min, command=self._on_slider_change)
        scale1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ===== SLIDER 2: Therapeutic Maximum (Green → Yellow boundary) =====
        frame2 = ttk.LabelFrame(parent, text="🟢 → 🟡  Therapeutic MAXIMUM", padding=12)
        frame2.pack(fill=tk.X, pady=8)
        
        desc2 = ttk.Label(frame2,
                         text="Pressure below this value = GREEN (therapeutic, optimal)\n"
                              "Pressure above this value = enters YELLOW zone (too high)",
                         font=('Arial', 8), foreground="gray", justify=tk.LEFT)
        desc2.pack(anchor=tk.W, pady=(0,5))
        
        self.var_max = tk.DoubleVar(value=self.current_zones['therapeutic_max'])
        
        slider_frame2 = ttk.Frame(frame2)
        slider_frame2.pack(fill=tk.X, pady=5)
        
        self.lbl_max = ttk.Label(slider_frame2, text=f"{self.var_max.get():.1f} kPa",
                                font=('Arial', 14, 'bold'), foreground="green", width=12)
        self.lbl_max.pack(side=tk.LEFT, padx=(0,10))
        
        scale2 = ttk.Scale(slider_frame2, from_=20, to=70, orient=tk.HORIZONTAL,
                          variable=self.var_max, command=self._on_slider_change)
        scale2.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ===== SLIDER 3: Caution Maximum (Yellow → Red boundary) =====
        frame3 = ttk.LabelFrame(parent, text="🟡 → 🔴  CAUTION Maximum", padding=12)
        frame3.pack(fill=tk.X, pady=8)
        
        desc3 = ttk.Label(frame3,
                         text="Pressure below this value = YELLOW (caution, above optimal)\n"
                              "Pressure above this value = RED (DANGER, tissue damage risk!)",
                         font=('Arial', 8), foreground="gray", justify=tk.LEFT)
        desc3.pack(anchor=tk.W, pady=(0,5))
        
        self.var_caut = tk.DoubleVar(value=self.current_zones['caution_max'])
        
        slider_frame3 = ttk.Frame(frame3)
        slider_frame3.pack(fill=tk.X, pady=5)
        
        self.lbl_caut = ttk.Label(slider_frame3, text=f"{self.var_caut.get():.1f} kPa",
                                 font=('Arial', 14, 'bold'), foreground="orange", width=12)
        self.lbl_caut.pack(side=tk.LEFT, padx=(0,10))
        
        scale3 = ttk.Scale(slider_frame3, from_=30, to=90, orient=tk.HORIZONTAL,
                          variable=self.var_caut, command=self._on_slider_change)
        scale3.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ===== CURRENT SETTINGS SUMMARY =====
        summary_frame = ttk.LabelFrame(parent, text="📋 Current Zone Settings", padding=10)
        summary_frame.pack(fill=tk.X, pady=(15,8))
        
        self.lbl_summary = ttk.Label(summary_frame, text="", font=('Arial', 9),
                                     justify=tk.LEFT)
        self.lbl_summary.pack()
        
        # ===== QUICK PRESETS =====
        preset_frame = ttk.LabelFrame(parent, text="🎯 Quick Presets (Common PT Techniques)", padding=10)
        preset_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(preset_frame, text="Click a preset to quickly set zones:",
                 font=('Arial', 8), foreground="gray").pack(anchor=tk.W, pady=(0,5))
        
        presets = [
            ("Standard PT (General)", 20, 45, 60),
            ("Soft Tissue Mobilization (Light)", 15, 35, 50),
            ("Joint Mobilization Grade IV (Strong)", 30, 55, 75),
            ("Lymphatic Drainage (Very Light)", 5, 15, 25)
        ]
        
        for name, min_v, max_v, caut_v in presets:
            btn = ttk.Button(preset_frame, text=name,
                           command=lambda m=min_v, mx=max_v, c=caut_v: self.apply_preset(m, mx, c))
            btn.pack(fill=tk.X, pady=2)
    
    def _create_preview(self, parent):
        """Create live preview panel with sample fingers"""
        ttk.Label(parent, text="Sample fingers at different pressures:",
                 font=('Arial', 10, 'bold')).pack(pady=(0,5))
        
        ttk.Label(parent, text="Watch how colors change as you drag sliders!",
                 font=('Arial', 9), foreground="blue").pack(pady=(0,10))
        
        # Matplotlib figure for preview
        self.preview_fig = Figure(figsize=(7, 9), dpi=85)
        self.preview_ax = self.preview_fig.add_subplot(111)
        
        self.preview_canvas = FigureCanvasTkAgg(self.preview_fig, parent)
        self.preview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _on_slider_change(self, value=None):
        """Called whenever any slider moves - updates everything in real-time"""
        # Update value labels
        self.lbl_min.config(text=f"{self.var_min.get():.1f} kPa")
        self.lbl_max.config(text=f"{self.var_max.get():.1f} kPa")
        self.lbl_caut.config(text=f"{self.var_caut.get():.1f} kPa")
        
        # Update temporary zones
        self.temp_zones['therapeutic_min'] = self.var_min.get()
        self.temp_zones['therapeutic_max'] = self.var_max.get()
        self.temp_zones['caution_max'] = self.var_caut.get()
        
        # Update summary text
        min_v = self.var_min.get()
        max_v = self.var_max.get()
        caut_v = self.var_caut.get()
        
        summary_text = (
            f"🔵 BLUE Zone:   < {min_v:.1f} kPa (Below therapeutic)\n"
            f"🟢 GREEN Zone:  {min_v:.1f} - {max_v:.1f} kPa (Therapeutic ✓)\n"
            f"🟡 YELLOW Zone: {max_v:.1f} - {caut_v:.1f} kPa (Above therapeutic)\n"
            f"🔴 RED Zone:    > {caut_v:.1f} kPa (DANGER!)"
        )
        self.lbl_summary.config(text=summary_text)
        
        # Update live preview - THIS IS THE KEY!
        self._update_preview()
    
    def _update_preview(self):
        """Update live preview with sample fingers at different pressures"""
        self.preview_ax.clear()
        self.preview_ax.set_xlim(0, 10)
        self.preview_ax.set_ylim(0, 15)
        self.preview_ax.set_aspect('equal')
        self.preview_ax.axis('off')
        self.preview_ax.set_title('Live Color Preview', fontsize=13, fontweight='bold', pad=10)
        
        # Sample pressures to display (covering full range)
        sample_pressures = [10, 20, 30, 40, 50, 60, 70]
        
        # Draw sample fingers showing different pressures
        for i, pressure in enumerate(sample_pressures):
            x = 1.3 * i + 0.3
            y = 2.5
            w = 1.0
            h = 7
            
            # Get color based on CURRENT zone settings (live!)
            color = self._get_color_for_pressure(pressure)
            zone_name = self._get_zone_name(pressure)
            
            # Draw finger rectangle
            rect = Rectangle((x, y), w, h,
                           facecolor=color, edgecolor='black',
                           linewidth=2.5, alpha=0.85)
            self.preview_ax.add_patch(rect)
            
            # Pressure value in center
            text_color = 'white' if pressure > 40 else 'black'
            self.preview_ax.text(x + w/2, y + h/2,
                               f"{pressure}\nkPa",
                               ha='center', va='center',
                               fontsize=12, fontweight='bold',
                               color=text_color)
            
            # Zone indicator below pressure
            self.preview_ax.text(x + w/2, y + h/2 - 1.2,
                               zone_name,
                               ha='center', va='top',
                               fontsize=8, fontweight='bold', style='italic',
                               color=text_color)
            
            # Pressure label above finger
            self.preview_ax.text(x + w/2, y + h + 0.3,
                               f"{pressure}",
                               ha='center', va='bottom',
                               fontsize=9, fontweight='bold')
        
        # ===== ZONE BOUNDARY VISUALIZATION BAR =====
        y_bar = 11
        
        self.preview_ax.text(0.3, y_bar + 1.8, 'Zone Boundaries:',
                            ha='left', fontsize=10, fontweight='bold')
        
        # Draw proportional zone bar
        x_start = 0.3
        x_total_width = 9.4
        max_pressure = 80  # Display range
        
        min_v = self.temp_zones['therapeutic_min']
        max_v = self.temp_zones['therapeutic_max']
        caut_v = self.temp_zones['caution_max']
        
        # Blue zone
        blue_width = (min_v / max_pressure) * x_total_width
        if blue_width > 0.1:
            rect = Rectangle((x_start, y_bar), blue_width, 0.6,
                            facecolor='#4A90E2', edgecolor='black', linewidth=2, alpha=0.8)
            self.preview_ax.add_patch(rect)
            if blue_width > 0.5:
                self.preview_ax.text(x_start + blue_width/2, y_bar + 0.3,
                                    'BLUE', ha='center', va='center',
                                    fontsize=8, fontweight='bold', color='white')
        
        # Green zone
        green_start = x_start + blue_width
        green_width = ((max_v - min_v) / max_pressure) * x_total_width
        if green_width > 0.1:
            rect = Rectangle((green_start, y_bar), green_width, 0.6,
                            facecolor='#4CAF50', edgecolor='black', linewidth=2, alpha=0.8)
            self.preview_ax.add_patch(rect)
            if green_width > 0.5:
                self.preview_ax.text(green_start + green_width/2, y_bar + 0.3,
                                    'GREEN', ha='center', va='center',
                                    fontsize=8, fontweight='bold', color='white')
        
        # Yellow zone
        yellow_start = green_start + green_width
        yellow_width = ((caut_v - max_v) / max_pressure) * x_total_width
        if yellow_width > 0.1:
            rect = Rectangle((yellow_start, y_bar), yellow_width, 0.6,
                            facecolor='#FFA726', edgecolor='black', linewidth=2, alpha=0.8)
            self.preview_ax.add_patch(rect)
            if yellow_width > 0.5:
                self.preview_ax.text(yellow_start + yellow_width/2, y_bar + 0.3,
                                    'YELLOW', ha='center', va='center',
                                    fontsize=8, fontweight='bold', color='white')
        
        # Red zone
        red_start = yellow_start + yellow_width
        red_width = ((max_pressure - caut_v) / max_pressure) * x_total_width
        if red_width > 0.1:
            rect = Rectangle((red_start, y_bar), red_width, 0.6,
                            facecolor='#EF5350', edgecolor='black', linewidth=2, alpha=0.8)
            self.preview_ax.add_patch(rect)
            if red_width > 0.5:
                self.preview_ax.text(red_start + red_width/2, y_bar + 0.3,
                                    'RED', ha='center', va='center',
                                    fontsize=8, fontweight='bold', color='white')
        
        # Boundary markers with values
        self.preview_ax.text(x_start, y_bar - 0.35, '0', ha='center', fontsize=8)
        self.preview_ax.plot([x_start + blue_width, x_start + blue_width], [y_bar - 0.2, y_bar], 'k-', linewidth=2)
        self.preview_ax.text(x_start + blue_width, y_bar - 0.35,
                            f'{min_v:.0f}', ha='center', fontsize=9, fontweight='bold')
        
        self.preview_ax.plot([green_start + green_width, green_start + green_width], [y_bar - 0.2, y_bar], 'k-', linewidth=2)
        self.preview_ax.text(green_start + green_width, y_bar - 0.35,
                            f'{max_v:.0f}', ha='center', fontsize=9, fontweight='bold')
        
        self.preview_ax.plot([yellow_start + yellow_width, yellow_start + yellow_width], [y_bar - 0.2, y_bar], 'k-', linewidth=2)
        self.preview_ax.text(yellow_start + yellow_width, y_bar - 0.35,
                            f'{caut_v:.0f}', ha='center', fontsize=9, fontweight='bold')
        
        self.preview_ax.text(x_start + x_total_width, y_bar - 0.35, '80', ha='center', fontsize=8)
        
        # Legend at bottom
        legend_y = 0.5
        self.preview_ax.text(0.3, legend_y, 
                            f'As you drag sliders, watch the sample fingers change color!',
                            ha='left', fontsize=8, style='italic', color='blue')
        
        self.preview_canvas.draw()
    
    def _get_color_for_pressure(self, pressure):
        """Get color for pressure value based on CURRENT temporary zones"""
        if pressure < 1:
            return '#E0E0E0'  # Gray for no contact
        elif pressure < self.temp_zones['therapeutic_min']:
            return '#4A90E2'  # Blue
        elif pressure <= self.temp_zones['therapeutic_max']:
            return '#4CAF50'  # Green
        elif pressure <= self.temp_zones['caution_max']:
            return '#FFA726'  # Yellow/Orange
        else:
            return '#EF5350'  # Red
    
    def _get_zone_name(self, pressure):
        """Get zone name for pressure value"""
        if pressure < 1:
            return "None"
        elif pressure < self.temp_zones['therapeutic_min']:
            return "Low"
        elif pressure <= self.temp_zones['therapeutic_max']:
            return "Good ✓"
        elif pressure <= self.temp_zones['caution_max']:
            return "High"
        else:
            return "Danger!"
    
    def apply_preset(self, min_v, max_v, caut_v):
        """Apply a quick preset - updates sliders and preview"""
        self.var_min.set(min_v)
        self.var_max.set(max_v)
        self.var_caut.set(caut_v)
        self._on_slider_change()  # Trigger update
    
    def reset_default(self):
        """Reset to default standard PT values"""
        self.apply_preset(20, 45, 60)
    
    def save_zones(self):
        """Validate and save the new zone settings"""
        min_v = self.var_min.get()
        max_v = self.var_max.get()
        caut_v = self.var_caut.get()
        
        # Validate: Min < Max < Caution
        if min_v >= max_v:
            messagebox.showerror("Invalid Values",
                f"Therapeutic MIN must be less than MAX!\n\n"
                f"Current: MIN={min_v:.1f}, MAX={max_v:.1f}\n"
                f"Please adjust sliders so MIN < MAX")
            return
        
        if max_v >= caut_v:
            messagebox.showerror("Invalid Values",
                f"Therapeutic MAX must be less than CAUTION!\n\n"
                f"Current: MAX={max_v:.1f}, CAUTION={caut_v:.1f}\n"
                f"Please adjust sliders so MAX < CAUTION")
            return
        
        # All valid - create new zones dict
        new_zones = {
            'therapeutic_min': min_v,
            'therapeutic_max': max_v,
            'caution_max': caut_v
        }
        
        # Call callback to update main app
        self.callback(new_zones)
        
        # Show confirmation
        messagebox.showinfo("✓ Zones Updated Successfully!",
            f"New pressure zones saved:\n\n"
            f"🔵 BLUE:   < {min_v:.1f} kPa\n"
            f"🟢 GREEN:  {min_v:.1f} - {max_v:.1f} kPa ✓\n"
            f"🟡 YELLOW: {max_v:.1f} - {caut_v:.1f} kPa\n"
            f"🔴 RED:    > {caut_v:.1f} kPa\n\n"
            f"Your visual hand display will now use these zones!")
        
        self.dialog.destroy()

# ============================================================================
# MAIN APPLICATION - TactileSense Clinical (v3.0 code with v3.1 configurator)
# ============================================================================

class TactileSenseClinical:
    """Clinical version with interactive zone configuration (v3.1)"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TactileSense v3.2 - Digital Master Record (DMR) Edition")
        self.root.geometry("1600x920")  # Slightly taller for DMR info bar
        
        # State
        self.sensor_mode = "disconnected"
        self.is_recording = False
        self.frame_count = 0
        self.current_pattern = "ball_grip"
        self.time_in_pattern = 0
        self.sensor_data = np.zeros(65, dtype=int)  # Raw sensor pulses (integers)
        self.display_data = np.zeros(65, dtype=int)  # What fingers display (frames when recording, pulses otherwise)
        
        # DMR session data - NEW in v3.2
        self.current_session_metadata = None
        self.recorded_frames = []
        self._session_saved = False   # set True after _save_dmr_file writes; forces new session on next Record
        self.auto_export_csv_var = None  # Created in UI, stores auto-export preference
        
        # Frame capture control - NEW: PT-adjustable frame frequency
        self.frame_period_ms = 50  # Default 50ms (20 Hz) - adjustable 20ms to 5000ms
        self.pulse_buffer = []  # Accumulates sensor readings for averaging
        self.last_frame_time = 0  # Timestamp of last frame capture
        self.frame_capture_scheduled = False  # Prevents duplicate frame capture scheduling
        
        # Hand orientation
        self.hand_orientation = {'roll': 0, 'pitch': 0, 'yaw': 0}
        
        # PT-DEFINED PRESSURE ZONES
        self.pressure_zones = {
            'therapeutic_min': 20,
            'therapeutic_max': 45,
            'caution_max': 60,
        }
        
        # Patterns
        self.patterns = {
            "idle": "No Activity",
            "ball_grip": "Ball Grip (Full Hand)",
            "precision_pinch": "Precision Pinch",
            "power_grip": "Power Grip",
            "pt_shoulder": "PT: Shoulder Mobilization",
            "pt_elbow": "PT: Elbow Mobilization",
            "pt_wrist": "PT: Wrist Manipulation",
            "three_finger": "Three-Finger Grip",
            "lateral_pinch": "Lateral Pinch"
        }
        
        self._create_ui()
        self.update_loop()
        
        print("✓ TactileSense v3.2 loaded!")
        print("✓ DMR save directory: " + self._get_default_dir())
        print("✓ PT zones: Blue < 20 < Green < 45 < Yellow < 60 < Red")
    
    # ------------------------------------------------------------------
    # FILE-SYSTEM HELPERS
    # ------------------------------------------------------------------
    def _get_default_dir(self):
        """Return (and create if needed) the base Protocols folder."""
        if os.name == 'nt':                          # Windows
            base = os.path.join(os.path.expanduser("~"), "TactileSense", "Protocols")
        else:                                        # macOS / Linux
            base = os.path.join(os.path.expanduser("~"), "TactileSense", "Protocols")
        
        # Create DMR subdirectories
        for sub in ("PT_Protocols", "PTA_Executions", "Robot_Executions"):
            os.makedirs(os.path.join(base, sub), exist_ok=True)
        
        # Create parallel CSV subdirectories
        csv_base = os.path.join(os.path.expanduser("~"), "TactileSense", "CSV_Exports")
        for sub in ("PT_CSV", "PTA_CSV", "Robot_CSV"):
            os.makedirs(os.path.join(csv_base, sub), exist_ok=True)
        
        return base

    def _pt_dir(self):
        return os.path.join(self._get_default_dir(), "PT_Protocols")

    def _pta_dir(self):
        return os.path.join(self._get_default_dir(), "PTA_Executions")
    
    def _pt_csv_dir(self):
        """PT protocol CSV export directory"""
        base = os.path.join(os.path.expanduser("~"), "TactileSense", "CSV_Exports")
        return os.path.join(base, "PT_CSV")
    
    def _pta_csv_dir(self):
        """PTA execution CSV export directory"""
        base = os.path.join(os.path.expanduser("~"), "TactileSense", "CSV_Exports")
        return os.path.join(base, "PTA_CSV")
    
    def _robot_csv_dir(self):
        """Robot execution CSV export directory"""
        base = os.path.join(os.path.expanduser("~"), "TactileSense", "CSV_Exports")
        return os.path.join(base, "Robot_CSV")
    
    def configure_zones(self):
        """Open NEW interactive zone configuration dialog with live preview"""
        def on_zones_updated(new_zones):
            self.pressure_zones = new_zones
            self.status_var.set(
                f"Zones updated: {new_zones['therapeutic_min']:.0f}-"
                f"{new_zones['therapeutic_max']:.0f}-{new_zones['caution_max']:.0f} kPa")
            print(f"✓ Zones: Blue<{new_zones['therapeutic_min']:.0f} "
                  f"Green:{new_zones['therapeutic_min']:.0f}-{new_zones['therapeutic_max']:.0f} "
                  f"Yellow:{new_zones['therapeutic_max']:.0f}-{new_zones['caution_max']:.0f} "
                  f"Red>{new_zones['caution_max']:.0f}")
        
        # Open interactive dialog
        InteractiveZoneDialog(self.root, self.pressure_zones, on_zones_updated)
    
    def _on_frame_period_change(self, value):
        """Callback when frame period slider changes"""
        period_ms = int(float(value))
        self.frame_period_ms = period_ms
        
        # Calculate frequency
        freq_hz = 1000.0 / period_ms
        
        # Update label
        if period_ms < 1000:
            self.lbl_frame_period.config(
                text=f"{period_ms} ms ({freq_hz:.1f} Hz) - averaging sensor pulses")
        else:
            period_sec = period_ms / 1000.0
            self.lbl_frame_period.config(
                text=f"{period_sec:.2f} sec ({freq_hz:.2f} Hz) - averaging sensor pulses")
    
    # All other methods from v3.0 follow below...
    # (Copying from baseline for completeness)
    
    def _create_ui(self):
        """Create UI - same as v3.0"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        sensor_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sensor", menu=sensor_menu)
        sensor_menu.add_command(label="🎭 Demo Simulator", command=self.connect_demo)
        sensor_menu.add_command(label="🧤 TactileGlove", command=self.connect_real)
        sensor_menu.add_separator()
        sensor_menu.add_command(label="❌ Disconnect", command=self.disconnect)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="⚙️ Pressure Zones (Interactive!)", command=self.configure_zones)
        settings_menu.add_command(label="🔄 Reset Orientation", command=self.reset_orientation)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_command(label="Export Data", command=self.export_data)
        
        dmr_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="DMR", menu=dmr_menu)
        dmr_menu.add_command(label="📋 View Current Session", command=self.view_session_info)
        dmr_menu.add_command(label="🎬 Review Frames",        command=self.view_frames)
        dmr_menu.add_command(label="📂 Load Previous DMR",   command=self.load_dmr)
        dmr_menu.add_command(label="📊 Export DMR Report",   command=self.export_dmr_report)
        dmr_menu.add_separator()
        dmr_menu.add_command(label="ℹ️  About DMR",           command=self.show_about_dmr)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Layout - same as v3.0
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left = ttk.Frame(main, width=250)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0,5))
        left.pack_propagate(False)
        
        mid_left = ttk.Frame(main)
        mid_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        mid_right = ttk.Frame(main, width=300)
        mid_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0,5))
        mid_right.pack_propagate(False)
        
        right = ttk.Frame(main, width=300)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right.pack_propagate(False)
        
        self._create_left_panel(left)
        self._create_hand_panel(mid_left)
        self._create_orientation_panel(mid_right)
        self._create_heatmap_panel(right)
        
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="TactileSense v3.2 DMR Edition — Select: Sensor → Demo Simulator or TactileGlove")
        ttk.Label(status_frame, textvariable=self.status_var,
                 relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.frame_var = tk.StringVar(value="Sensor: 0")
        ttk.Label(status_frame, textvariable=self.frame_var,
                 relief=tk.SUNKEN, width=15).pack(side=tk.RIGHT)
        
        # DMR session info bar (NEW — was missing entirely)
        self.dmr_session_widget = DMRSessionInfo(self.root)
        self.dmr_session_widget.pack(fill=tk.X, padx=5, pady=(2, 0), before=status_frame)
    
    def _create_left_panel(self, parent):
        """Create left control panel - same as v3.0"""
        mode_box = ttk.LabelFrame(parent, text="Mode", padding=10)
        mode_box.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_mode = ttk.Label(mode_box, text="⚠ NOT\nCONNECTED",
                                  font=('Arial', 10, 'bold'), foreground="red", justify=tk.CENTER)
        self.lbl_mode.pack()
        
        zones_box = ttk.LabelFrame(parent, text="📊 Pressure Zones", padding=8)
        zones_box.pack(fill=tk.X, padx=5, pady=5)
        
        zone_info = [
            ("🔵 Blue", "< 20 kPa", "Below therapeutic", "blue"),
            ("🟢 Green", "20-45 kPa", "Therapeutic range", "green"),
            ("🟡 Yellow", "45-60 kPa", "Above therapeutic", "orange"),
            ("🔴 Red", "> 60 kPa", "Dangerous/too high", "red")
        ]
        
        for emoji, range_text, desc, color in zone_info:
            frame = ttk.Frame(zones_box)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=emoji, font=('Arial', 10)).pack(side=tk.LEFT)
            info_frame = ttk.Frame(frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
            ttk.Label(info_frame, text=range_text, font=('Arial', 8, 'bold'),
                     foreground=color).pack(anchor=tk.W)
            ttk.Label(info_frame, text=desc, font=('Arial', 7)).pack(anchor=tk.W)
        
        ttk.Button(zones_box, text="⚙️ Configure Zones (Interactive!)",
                  command=self.configure_zones).pack(fill=tk.X, pady=(5,0))
        
        self.demo_container = ttk.Frame(parent)
        
        pattern_box = ttk.LabelFrame(self.demo_container, text="📋 Patterns", padding=8)
        pattern_box.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pattern_box, text="Select:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        self.pattern_var = tk.StringVar(value="ball_grip")
        
        scroll_frame = ttk.Frame(pattern_box)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame, height=120, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas)
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for key, name in self.patterns.items():
            ttk.Radiobutton(content, text=name, variable=self.pattern_var,
                          value=key, command=self.change_pattern).pack(anchor=tk.W, pady=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        rec_box = ttk.LabelFrame(parent, text="DMR Controls", padding=8)
        rec_box.pack(fill=tk.X, padx=5, pady=5)
        
        btn_row = ttk.Frame(rec_box)
        btn_row.pack(fill=tk.X)
        
        self.btn_rec = ttk.Button(btn_row, text="⏺ Record", command=self.toggle_record, width=12)
        self.btn_rec.pack(side=tk.LEFT, padx=2)
        
        self.btn_stop = ttk.Button(btn_row, text="⏹ Stop & Save", command=self.stop_record,
                                   width=14, state="disabled")
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        
        self.lbl_rec = ttk.Label(rec_box, text="Click ⏺ Record to start a DMR session",
                                 foreground="gray", font=('Arial', 8))
        self.lbl_rec.pack(pady=2)
        
        # Visual separator
        ttk.Separator(rec_box, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        
        # Section header for auto-export
        ttk.Label(rec_box, text="Export Settings:",
                 font=('Arial', 9, 'bold'),
                 foreground="darkblue").pack(anchor=tk.W, pady=(0,5))
        
        # Auto-export option
        self.auto_export_csv_var = tk.BooleanVar(value=True)  # Default ON
        
        cb_export = ttk.Checkbutton(rec_box,
                                     text="💾 Auto-export CSV when saving",
                                     variable=self.auto_export_csv_var)
        cb_export.pack(anchor=tk.W, padx=5, pady=(0,3))
        
        ttk.Label(rec_box,
                 text="(CSV automatically saved to CSV_Exports folder)",
                 font=('Arial', 7),
                 foreground="gray").pack(anchor=tk.W, padx=25)
        
        # Debug confirmation
        print("✓ Auto-export CSV checkbox created in DMR Controls")
        
        # Frame capture frequency control
        ttk.Separator(rec_box, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        
        ttk.Label(rec_box, text="Frame Capture Period:",
                 font=('Arial', 9, 'bold'),
                 foreground="darkblue").pack(anchor=tk.W, pady=(0,5))
        
        frame_control = ttk.Frame(rec_box)
        frame_control.pack(fill=tk.X, padx=5, pady=(0,5))
        
        # Frame period slider (20ms to 5000ms)
        self.frame_period_var = tk.IntVar(value=50)  # Default 50ms
        
        slider_frame = ttk.Frame(frame_control)
        slider_frame.pack(fill=tk.X)
        
        ttk.Label(slider_frame, text="Fast", font=('Arial', 7)).pack(side=tk.LEFT, padx=(0,5))
        
        self.frame_period_slider = ttk.Scale(slider_frame, from_=20, to=5000,
                                             orient=tk.HORIZONTAL,
                                             variable=self.frame_period_var,
                                             command=self._on_frame_period_change)
        self.frame_period_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(slider_frame, text="Slow", font=('Arial', 7)).pack(side=tk.LEFT, padx=(5,0))
        
        # Display current value
        self.lbl_frame_period = ttk.Label(frame_control,
                                          text="50 ms (20.0 Hz) - averaging sensor pulses",
                                          font=('Arial', 8),
                                          foreground="darkgreen")
        self.lbl_frame_period.pack(anchor=tk.W, pady=(3,0))
        
        print("✓ Frame capture period control created")
        
        stats_box = ttk.LabelFrame(parent, text="📊 Stats", padding=8)
        stats_box.pack(fill=tk.X, padx=5, pady=5)
        
        grid = ttk.Frame(stats_box)
        grid.pack()
        
        ttk.Label(grid, text="Peak:", font=('Arial', 8)).grid(row=0, column=0, sticky=tk.W)
        self.lbl_peak = ttk.Label(grid, text="0.0 kPa", font=('Arial', 9, 'bold'))
        self.lbl_peak.grid(row=0, column=1, sticky=tk.W, padx=(3,0))
        
        ttk.Label(grid, text="Avg:", font=('Arial', 8)).grid(row=1, column=0, sticky=tk.W)
        self.lbl_avg = ttk.Label(grid, text="0.0 kPa", font=('Arial', 8))
        self.lbl_avg.grid(row=1, column=1, sticky=tk.W, padx=(3,0))
        
        ttk.Label(grid, text="In Zone:", font=('Arial', 8)).grid(row=2, column=0, sticky=tk.W)
        self.lbl_zone = ttk.Label(grid, text="N/A", font=('Arial', 8, 'bold'), foreground="gray")
        self.lbl_zone.grid(row=2, column=1, sticky=tk.W, padx=(3,0))
        
        ttk.Separator(grid, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky='ew', pady=3)
        
        ttk.Label(grid, text="Active:", font=('Arial', 8)).grid(row=4, column=0, sticky=tk.W)
        self.lbl_active = ttk.Label(grid, text="0/65", font=('Arial', 8))
        self.lbl_active.grid(row=4, column=1, sticky=tk.W, padx=(3,0))
    
    def _create_hand_panel(self, parent):
        """Create visual hand panel - same as v3.0"""
        self.hand_container = ttk.LabelFrame(parent, text="👋 Visual Tactile Glove (PT Zones)", padding=10)
        
        self.hand_fig = Figure(figsize=(10, 11), dpi=90)
        self.hand_ax = self.hand_fig.add_subplot(111)
        self.hand_canvas = FigureCanvasTkAgg(self.hand_fig, self.hand_container)
        self.hand_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.disconnected_frame = ttk.Frame(parent)
        self.disconnected_frame.pack(fill=tk.BOTH, expand=True)
        
        msg = ttk.LabelFrame(self.disconnected_frame, text="Welcome", padding=20)
        msg.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(msg, text="TactileSense v3.1", font=('Arial', 20, 'bold')).pack(pady=10)
        ttk.Label(msg, text="Digital Master Record (DMR) Edition", font=('Arial', 12)).pack(pady=5)
        ttk.Label(msg, text="Select: Sensor → Demo or TactileGlove",
                 font=('Arial', 11)).pack(pady=10)
    
    def _create_orientation_panel(self, parent):
        """Create 3D orientation panel - same as v3.0"""
        self.orient_container = ttk.LabelFrame(parent, text="🔄 Hand Orientation (3D)", padding=8)
        
        self.orient_fig = Figure(figsize=(4, 6), dpi=80)
        self.orient_ax = self.orient_fig.add_subplot(111, projection='3d')
        self.orient_canvas = FigureCanvasTkAgg(self.orient_fig, self.orient_container)
        self.orient_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.Frame(self.orient_container)
        control_frame.pack(fill=tk.X, pady=(5,0))
        
        ttk.Label(control_frame, text="Roll:", font=('Arial', 8)).grid(row=0, column=0, sticky=tk.W)
        self.lbl_roll = ttk.Label(control_frame, text="0°", font=('Arial', 8, 'bold'))
        self.lbl_roll.grid(row=0, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(control_frame, text="Pitch:", font=('Arial', 8)).grid(row=1, column=0, sticky=tk.W)
        self.lbl_pitch = ttk.Label(control_frame, text="0°", font=('Arial', 8, 'bold'))
        self.lbl_pitch.grid(row=1, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Label(control_frame, text="Yaw:", font=('Arial', 8)).grid(row=2, column=0, sticky=tk.W)
        self.lbl_yaw = ttk.Label(control_frame, text="0°", font=('Arial', 8, 'bold'))
        self.lbl_yaw.grid(row=2, column=1, sticky=tk.W, padx=(5,0))
        
        ttk.Button(control_frame, text="Reset", command=self.reset_orientation,
                  width=10).grid(row=3, column=0, columnspan=2, pady=(5,0))
        
        note = ttk.Label(self.orient_container,
                        text="Shows hand position\nin 3D space",
                        font=('Arial', 7), foreground="gray", justify=tk.CENTER)
        note.pack(pady=(5,0))
    
    def _create_heatmap_panel(self, parent):
        """Create heatmap panel - same as v3.0"""
        heat_box = ttk.LabelFrame(parent, text="🔥 Pressure Map", padding=8)
        heat_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.heat_fig = Figure(figsize=(3.5, 9), dpi=85)
        self.heat_ax = self.heat_fig.add_subplot(111)
        self.heat_canvas = FigureCanvasTkAgg(self.heat_fig, heat_box)
        self.heat_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_heatmap()
    
    def get_pressure_zone_color(self, pressure):
        """Get color based on PT zones - same as v3.0"""
        if pressure < 1:
            return '#E0E0E0'
        elif pressure < self.pressure_zones['therapeutic_min']:
            return '#4A90E2'
        elif pressure <= self.pressure_zones['therapeutic_max']:
            return '#4CAF50'
        elif pressure <= self.pressure_zones['caution_max']:
            return '#FFA726'
        else:
            return '#EF5350'
    
    def get_zone_name(self, pressure):
        """Get zone name - same as v3.0"""
        if pressure < 1:
            return "No Contact"
        elif pressure < self.pressure_zones['therapeutic_min']:
            return "Below Therapeutic"
        elif pressure <= self.pressure_zones['therapeutic_max']:
            return "Therapeutic ✓"
        elif pressure <= self.pressure_zones['caution_max']:
            return "Above Therapeutic"
        else:
            return "CAUTION!"
    
    # [Continuing with all drawing and update methods from v3.0...]
    # Due to length limits, including key methods below:
    
    def draw_hand(self):
        """Draw visual hand - same as v3.0"""
        if self.sensor_mode != "demo":
            return
        
        self.hand_ax.clear()
        self.hand_ax.set_xlim(0, 10)
        self.hand_ax.set_ylim(0, 16)
        self.hand_ax.set_aspect('equal')
        self.hand_ax.axis('off')
        self.hand_ax.set_title('Tactile Glove - PT Pressure Zones',
                              fontsize=14, fontweight='bold', pad=10)
        
        fingers = [
            {'x': 0.5, 'y': 2, 'w': 2, 'h': 8, 'name': 'Thumb', 'idx': range(0, 13)},
            {'x': 2.8, 'y': 7, 'w': 1.6, 'h': 8, 'name': 'Index', 'idx': range(13, 26)},
            {'x': 4.6, 'y': 8, 'w': 1.6, 'h': 8, 'name': 'Middle', 'idx': range(26, 39)},
            {'x': 6.4, 'y': 7.5, 'w': 1.6, 'h': 7.5, 'name': 'Ring', 'idx': range(39, 52)},
            {'x': 8.2, 'y': 6, 'w': 1.5, 'h': 6, 'name': 'Pinky', 'idx': range(52, 65)}
        ]
        
        for f in fingers:
            p = np.mean(self.display_data[list(f['idx'])])  # Use display_data to show frames when recording
            color = self.get_pressure_zone_color(p)
            
            rect = Rectangle((f['x'], f['y']), f['w'], f['h'],
                           facecolor=color, edgecolor='black', linewidth=3, alpha=0.8)
            self.hand_ax.add_patch(rect)
            
            self.hand_ax.text(f['x'] + f['w']/2, f['y'] + f['h'] + 0.4,
                            f['name'], ha='center', fontsize=11, fontweight='bold')
            
            self.hand_ax.text(f['x'] + f['w']/2, f['y'] + f['h']/2,
                            f"{p:.1f}\nkPa", ha='center', va='center',
                            fontsize=13, fontweight='bold',
                            color='white' if p > 30 else 'black')
            
            zone = self.get_zone_name(p)
            self.hand_ax.text(f['x'] + f['w']/2, f['y'] + f['h']/2 - 1,
                            zone, ha='center', va='top',
                            fontsize=7, style='italic',
                            color='white' if p > 30 else 'black')
        
        palm = Rectangle((2.5, 0.5), 6, 2, facecolor='#D3D3D3',
                        edgecolor='black', linewidth=3, alpha=0.6)
        self.hand_ax.add_patch(palm)
        self.hand_ax.text(5.5, 1.5, 'PALM', ha='center', va='center',
                         fontsize=11, fontweight='bold', style='italic')
        
        y_start = 0.2
        self.hand_ax.text(0.5, y_start - 0.3, 'PT Zones:', ha='left',
                         fontsize=9, fontweight='bold')
        
        zones = [
            ('#E0E0E0', 'No Contact'),
            ('#4A90E2', f'< {self.pressure_zones["therapeutic_min"]:.0f} (Low)'),
            ('#4CAF50', f'{self.pressure_zones["therapeutic_min"]:.0f}-{self.pressure_zones["therapeutic_max"]:.0f} (Good)'),
            ('#FFA726', f'{self.pressure_zones["therapeutic_max"]:.0f}-{self.pressure_zones["caution_max"]:.0f} (High)'),
            ('#EF5350', f'> {self.pressure_zones["caution_max"]:.0f} (Danger)')
        ]
        
        for i, (color, label) in enumerate(zones):
            x = 0.5 + i * 1.8
            rect = Rectangle((x, y_start), 0.35, 0.35, facecolor=color, edgecolor='black', linewidth=1.5)
            self.hand_ax.add_patch(rect)
            self.hand_ax.text(x + 0.175, y_start - 0.2, label, ha='center', fontsize=6.5)
        
        self.hand_canvas.draw()
    
    def draw_orientation(self):
        """Draw 3D orientation - same as v3.0"""
        if self.sensor_mode == "disconnected":
            return
        
        self.orient_ax.clear()
        self.orient_ax.set_xlim([-1.5, 1.5])
        self.orient_ax.set_ylim([-1.5, 1.5])
        self.orient_ax.set_zlim([-1.5, 1.5])
        self.orient_ax.set_xlabel('X', fontsize=9, fontweight='bold')
        self.orient_ax.set_ylabel('Y', fontsize=9, fontweight='bold')
        self.orient_ax.set_zlabel('Z', fontsize=9, fontweight='bold')
        self.orient_ax.set_title('Hand Orientation', fontsize=10, fontweight='bold')
        
        roll = np.radians(self.hand_orientation['roll'])
        pitch = np.radians(self.hand_orientation['pitch'])
        yaw = np.radians(self.hand_orientation['yaw'])
        
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(roll), -np.sin(roll)],
                       [0, np.sin(roll), np.cos(roll)]])
        
        Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                       [0, 1, 0],
                       [-np.sin(pitch), 0, np.cos(pitch)]])
        
        Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                       [np.sin(yaw), np.cos(yaw), 0],
                       [0, 0, 1]])
        
        R = Rz @ Ry @ Rx
        
        axes_length = 1.2
        x_axis = np.array([axes_length, 0, 0])
        y_axis = np.array([0, axes_length, 0])
        z_axis = np.array([0, 0, axes_length])
        
        x_rot = R @ x_axis
        y_rot = R @ y_axis
        z_rot = R @ z_axis
        
        origin = [0, 0, 0]
        
        self.orient_ax.quiver(origin[0], origin[1], origin[2],
                             x_rot[0], x_rot[1], x_rot[2],
                             color='red', arrow_length_ratio=0.2, linewidth=3)
        self.orient_ax.text(x_rot[0]*1.1, x_rot[1]*1.1, x_rot[2]*1.1,
                           'X (Fingers)', color='red', fontsize=8, fontweight='bold')
        
        self.orient_ax.quiver(origin[0], origin[1], origin[2],
                             y_rot[0], y_rot[1], y_rot[2],
                             color='green', arrow_length_ratio=0.2, linewidth=3)
        self.orient_ax.text(y_rot[0]*1.1, y_rot[1]*1.1, y_rot[2]*1.1,
                           'Y (Palm)', color='green', fontsize=8, fontweight='bold')
        
        self.orient_ax.quiver(origin[0], origin[1], origin[2],
                             z_rot[0], z_rot[1], z_rot[2],
                             color='blue', arrow_length_ratio=0.2, linewidth=3)
        self.orient_ax.text(z_rot[0]*1.1, z_rot[1]*1.1, z_rot[2]*1.1,
                           'Z (Normal)', color='blue', fontsize=8, fontweight='bold')
        
        self.orient_ax.quiver(0, 0, 0, 0.5, 0, 0, color='red', alpha=0.2, linewidth=1)
        self.orient_ax.quiver(0, 0, 0, 0, 0.5, 0, color='green', alpha=0.2, linewidth=1)
        self.orient_ax.quiver(0, 0, 0, 0, 0, 0.5, color='blue', alpha=0.2, linewidth=1)
        
        self.orient_ax.view_init(elev=20, azim=45)
        
        self.orient_canvas.draw()
        
        self.lbl_roll.config(text=f"{self.hand_orientation['roll']:.1f}°")
        self.lbl_pitch.config(text=f"{self.hand_orientation['pitch']:.1f}°")
        self.lbl_yaw.config(text=f"{self.hand_orientation['yaw']:.1f}°")
    
    def update_hand_orientation(self):
        """Update orientation - same as v3.0"""
        if self.sensor_mode == "demo":
            t = self.time_in_pattern / 100.0
            self.hand_orientation['roll'] = 15 * np.sin(0.5 * t)
            self.hand_orientation['pitch'] = 10 * np.sin(0.3 * t + 1)
            self.hand_orientation['yaw'] = 20 * np.sin(0.2 * t + 2)
    
    def reset_orientation(self):
        """Reset orientation - same as v3.0"""
        self.hand_orientation = {'roll': 0, 'pitch': 0, 'yaw': 0}
        self.draw_orientation()
        messagebox.showinfo("Orientation Reset", "Hand orientation reset to 0°, 0°, 0°")
    
    def connect_demo(self):
        """Connect demo - same as v3.0"""
        if self.sensor_mode == "demo":
            # Already in demo — nothing to do
            return
        if self.sensor_mode != "disconnected":
            if not messagebox.askyesno("Switch?", "Switch to Demo?"):
                return
            self.disconnect()
        
        self.sensor_mode = "demo"
        self.current_pattern = "ball_grip"
        self.time_in_pattern = 0
        
        self.lbl_mode.config(text="🎭 DEMO\nMODE", foreground="blue")
        self.demo_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.disconnected_frame.pack_forget()
        self.hand_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.orient_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_var.set("Demo mode - Try Settings → Pressure Zones (Interactive!)")
        
        messagebox.showinfo("Demo Mode",
            "🎭 DEMO MODE\n\n"
            "✓ PT pressure zones active\n"
            "✓ 3D orientation display\n"
            "✓ NEW: Interactive zone config!\n\n"
            "Try: Settings → Pressure Zones\n"
            "to see live visual feedback!")
        
        print("✓ Demo mode active")
    
    def connect_real(self):
        """Connect real glove - same as v3.0"""
        if self.sensor_mode != "disconnected":
            if not messagebox.askyesno("Switch?", "Switch to TactileGlove?"):
                return
            self.disconnect()
        
        self.sensor_mode = "real_glove"
        
        self.lbl_mode.config(text="🧤 GLOVE\nMODE", foreground="green")
        self.demo_container.pack_forget()
        self.hand_container.pack_forget()
        self.disconnected_frame.pack(fill=tk.BOTH, expand=True)
        self.orient_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_var.set("TactileGlove mode")
        
        messagebox.showinfo("TactileGlove", "🧤 Ready for real hardware!")
        
        print("✓ TactileGlove mode")
    
    def disconnect(self):
        """Disconnect sensor.  If a DMR session is actively recording, pause it
        first so reconnecting does not silently resume frame capture."""
        # --- pause any live recording before we go dark -----------------
        if self.is_recording and self.current_session_metadata:
            self.is_recording = False
            self.frame_capture_scheduled = False  # Stop frame capture
            self.pulse_buffer.clear()  # Clear accumulated pulses
            self.btn_rec.config(text="⏺ Resume")
            # btn_stop stays enabled — session is still open, user can
            # resume after reconnecting or click Stop & Save now.
            self.lbl_rec.config(
                text=f"⏸ PAUSED (disconnected)\n"
                     f"Reconnect sensor, then Resume or Stop & Save",
                foreground="darkorange")
            self.status_var.set(
                "⏸ Recording PAUSED — sensor disconnected. "
                "Reconnect to resume, or click ⏹ Stop & Save.")

        self.sensor_mode = "disconnected"
        self.sensor_data = np.zeros(65, dtype=int)
        self.display_data = np.zeros(65, dtype=int)
        
        self.lbl_mode.config(text="⚠ NOT\nCONNECTED", foreground="red")
        self.demo_container.pack_forget()
        self.hand_container.pack_forget()
        self.orient_container.pack_forget()
        
        if not self.disconnected_frame.winfo_ismapped():
            self.disconnected_frame.pack(fill=tk.BOTH, expand=True)
        
        if not (self.is_recording and self.current_session_metadata):
            # Only overwrite status if we didn't just set the paused message
            self.status_var.set("Disconnected")
        self.update_heatmap()
        self.update_stats()
    
    def change_pattern(self):
        """Change pattern - same as v3.0"""
        if self.sensor_mode == "demo":
            self.current_pattern = self.pattern_var.get()
            self.time_in_pattern = 0
            self.status_var.set(f"Pattern: {self.patterns[self.current_pattern]}")
    
    def generate_data(self):
        """Generate sensor data as INTEGERS (kPa values)"""
        if self.sensor_mode == "disconnected":
            return np.zeros(65, dtype=int)
        
        t = self.time_in_pattern / 100.0
        
        if self.sensor_mode == "demo":
            pattern = self.current_pattern
            
            if pattern == "idle":
                return np.zeros(65, dtype=int)
            elif pattern == "ball_grip":
                data = np.zeros(65)
                for i in range(5):
                    start = i * 13
                    p = 35 + 10 * np.sin(2 * np.pi * 0.3 * t)
                    for j in range(13):
                        f = 1.0 - (j / 13) * 0.4
                        data[start + j] = p * f + np.random.normal(0, 2)
                return np.maximum(0, data).astype(int)
            elif pattern == "precision_pinch":
                data = np.zeros(65)
                p = 40 + 5 * np.sin(2 * np.pi * 0.5 * t)
                data[0:6] = p + np.random.normal(0, 3, 6)
                data[13:19] = p + np.random.normal(0, 3, 6)
                return np.maximum(0, data).astype(int)
            elif pattern == "power_grip":
                data = np.zeros(65)
                for i in range(5):
                    start = i * 13
                    base = 50 + 8 * np.sin(2 * np.pi * 0.2 * t)
                    for j in range(13):
                        f = 1.0 - abs(j - 6) / 10
                        data[start + j] = base * f + np.random.normal(0, 3)
                return np.maximum(0, data).astype(int)
            elif pattern == "pt_shoulder":
                data = np.zeros(65)
                data[0:13] = 30 + np.random.normal(0, 2, 13)
                pulse = 35 + 15 * np.sin(2 * np.pi * 0.8 * t)
                data[13:26] = pulse + np.random.normal(0, 3, 13)
                data[26:39] = pulse * 0.85 + np.random.normal(0, 3, 13)
                data[39:65] = np.random.uniform(0, 8, 26)
                return np.maximum(0, data).astype(int)
            elif pattern == "pt_elbow":
                data = np.zeros(65)
                data[0:13] = 25 + np.random.normal(0, 2, 13)
                pulse = 30 + 12 * np.sin(2 * np.pi * 0.6 * t)
                data[13:52] = pulse + np.random.normal(0, 3, 39)
                data[52:65] = 10 + np.random.normal(0, 2, 13)
                return np.maximum(0, data).astype(int)
            elif pattern == "pt_wrist":
                data = np.zeros(65)
                t2 = t * 2
                data[0:13] = 28 + 8 * np.sin(2 * np.pi * 0.7 * t2) + np.random.normal(0, 2, 13)
                data[13:26] = 38 + 10 * np.sin(2 * np.pi * 0.7 * t2 + 0.5) + np.random.normal(0, 2, 13)
                data[26:65] = np.random.uniform(5, 15, 39)
                return np.maximum(0, data).astype(int)
            elif pattern == "three_finger":
                data = np.zeros(65)
                p = 35 + 8 * np.sin(2 * np.pi * 0.4 * t)
                data[0:39] = p + np.random.normal(0, 3, 39)
                return np.maximum(0, data).astype(int)
            elif pattern == "lateral_pinch":
                data = np.zeros(65)
                data[0:13] = 42 + np.random.normal(0, 3, 13)
                data[17:23] = 40 + np.random.normal(0, 3, 6)
                return np.maximum(0, data).astype(int)
        
        else:  # real_glove
            base = np.random.uniform(0, 20, 65)
            var = 10 * np.sin(2 * np.pi * 0.5 * t)
            for i in range(5):
                start = i * 13
                end = start + 13
                base[start:end] += var * (1 + i/5)
            return np.maximum(0, base + np.random.normal(0, 0.5, 65)).astype(int)
        
        return np.zeros(65, dtype=int)
    
    def update_heatmap(self):
        """Update heatmap - displays FRAMES when recording, pulses otherwise"""
        self.heat_ax.clear()
        
        grid = self.display_data.reshape((13, 5))  # Use display_data, not sensor_data
        
        im = self.heat_ax.imshow(grid, cmap='hot', interpolation='bilinear',
                                vmin=0, vmax=60, aspect='auto')
        
        self.heat_ax.set_title('Pressure', fontsize=10, fontweight='bold')
        self.heat_ax.set_xlabel('Finger', fontsize=8)
        self.heat_ax.set_ylabel('Row', fontsize=8)
        
        labels = ['Th', 'Idx', 'Mid', 'Rng', 'Pnk']
        self.heat_ax.set_xticks(range(5))
        self.heat_ax.set_xticklabels(labels, fontsize=7)
        self.heat_ax.tick_params(axis='y', labelsize=7)
        
        if not hasattr(self, 'colorbar'):
            self.colorbar = self.heat_fig.colorbar(im, ax=self.heat_ax)
            self.colorbar.set_label('kPa', rotation=0, labelpad=8, fontsize=8)
            self.colorbar.ax.tick_params(labelsize=7)
        
        self.heat_canvas.draw()
    
    def update_stats(self):
        """Update stats - displays FRAME stats when recording, pulse stats otherwise"""
        active = self.display_data > 1.0  # Use display_data, not sensor_data
        
        if np.any(active):
            peak = np.max(self.display_data)
            avg = np.mean(self.display_data[active])
            n = np.sum(active)
            
            zone = self.get_zone_name(avg)
            zone_color = self.get_pressure_zone_color(avg)
            
            color_map = {
                '#4A90E2': 'blue',
                '#4CAF50': 'green',
                '#FFA726': 'orange',
                '#EF5350': 'red',
                '#E0E0E0': 'gray'
            }
            display_color = color_map.get(zone_color, 'black')
            
        else:
            peak = avg = n = 0
            zone = "N/A"
            display_color = "gray"
        
        self.lbl_peak.config(text=f"{peak:.1f} kPa")
        self.lbl_avg.config(text=f"{avg:.1f} kPa")
        self.lbl_zone.config(text=zone, foreground=display_color)
        self.lbl_active.config(text=f"{int(n)}/65")
    
    def update_loop(self):
        """
        Update loop - runs at 50ms for sensor sampling and display.
        Frame capture happens at PT-adjustable rate with pulse averaging.
        Fingers display FRAMES when recording, raw PULSES when not recording.
        """
        if self.sensor_mode != "disconnected":
            self.sensor_data = self.generate_data()
            
            # Set what the display shows:
            # - When NOT recording: show raw sensor pulses (real-time feedback)
            # - When recording: show frames (updated in _capture_frame)
            if not self.is_recording:
                self.display_data = self.sensor_data.copy()
            # else: display_data is updated by _capture_frame to show frames
            
            # Accumulate sensor pulses for averaging (if recording)
            if self.is_recording and self.current_session_metadata:
                self.pulse_buffer.append(self.sensor_data.copy())
                
                # Schedule frame capture if not already scheduled
                if not self.frame_capture_scheduled:
                    self.frame_capture_scheduled = True
                    self.root.after(self.frame_period_ms, self._capture_frame)
            
            # Update display (sensor mode specific)
            if self.sensor_mode == "demo":
                self.draw_hand()
                self.update_hand_orientation()
            
            self.draw_orientation()
            self.update_heatmap()
            self.update_stats()
            
            self.frame_count += 1
            self.time_in_pattern += 1
            self.frame_var.set(f"Sensor: {self.frame_count}")
        
        # Continue sensor update loop at 50ms
        self.root.after(50, self.update_loop)
    
    def _capture_frame(self):
        """
        Capture a DMR frame by averaging accumulated sensor pulses.
        Called at PT-adjustable frame period (20ms to 5000ms).
        Updates display_data so fingers show FRAMES, not raw pulses.
        """
        if not self.is_recording or not self.current_session_metadata:
            self.frame_capture_scheduled = False
            self.pulse_buffer.clear()
            return
        
        try:
            # Average accumulated sensor pulses and convert to integers
            if self.pulse_buffer:
                averaged_data = np.mean(self.pulse_buffer, axis=0).astype(int)
                num_pulses = len(self.pulse_buffer)
                self.pulse_buffer.clear()
            else:
                # No pulses accumulated (shouldn't happen), use current data
                averaged_data = self.sensor_data.astype(int)
                num_pulses = 1
            
            # Update display_data with this frame (fingers now show frames, not pulses)
            self.display_data = averaged_data.copy()
            
            # Create frame with integer data
            frame_data = {
                'frame_number': len(self.recorded_frames),
                'timestamp': datetime.now().isoformat(),
                'sensor_data': averaged_data.tolist(),  # Integers
                'hand_orientation': self.hand_orientation.copy(),
                'demo_pattern': self.current_pattern if self.sensor_mode == "demo" else None,
                'frame_period_ms': self.frame_period_ms,  # Record the frame period used
                'pulses_averaged': num_pulses  # How many sensor samples averaged
            }
            self.recorded_frames.append(frame_data)
            
            # Debug output
            if len(self.recorded_frames) % 10 == 0:  # Every 10th frame
                print(f"✓ Frame {len(self.recorded_frames)} captured "
                      f"(averaged {num_pulses} pulses, period: {self.frame_period_ms}ms)")
            
            # Update live frame counter
            self.lbl_rec.config(
                text=f"🔴 Recording  DMR Frames: {len(self.recorded_frames)}",
                foreground="red")
            
            # Schedule next frame capture if still recording
            if self.is_recording and self.current_session_metadata:
                self.root.after(self.frame_period_ms, self._capture_frame)
            else:
                self.frame_capture_scheduled = False
                
        except Exception as e:
            print(f"✗ ERROR in _capture_frame: {e}")
            import traceback
            traceback.print_exc()
            self.frame_capture_scheduled = False
    
    def toggle_record(self):
        """Toggle recording — RESUME if paused, NEW session if none exists or previous was saved"""
        if self.sensor_mode == "disconnected":
            messagebox.showwarning("Sensor Not Connected",
                "Please connect a sensor before starting a DMR session.\n\n"
                "Sensor menu → Demo Simulator or TactileGlove")
            return
        
        if self.is_recording:
            # Currently recording → pause
            self.is_recording = False
            self.frame_capture_scheduled = False  # Stop frame capture
            self.pulse_buffer.clear()  # Clear accumulated pulses
            self.btn_rec.config(text="⏺ Resume")
            self.status_var.set("Recording PAUSED — click ⏺ Resume or ⏹ Stop & Save")
        elif self.current_session_metadata and not self._session_saved:
            # Paused with an active session that has NOT been saved → resume it
            self.is_recording = True
            self.btn_rec.config(text="⏸ Pause")
            self.btn_stop.config(state="normal")
            self.status_var.set(
                f"Recording RESUMED — {self.current_session_metadata['session_id']}")
            # Note: frame capture will auto-restart in update_loop
        else:
            # No session, OR previous session was already saved → start fresh
            self.current_session_metadata = None
            self.recorded_frames = []
            self._session_saved = False
            self.dmr_session_widget.clear_session()
            self._start_dmr_session()
    
    def _start_dmr_session(self):
        """Start new DMR session with metadata capture"""
        def on_session_created(metadata):
            if metadata:
                # Store session metadata
                self.current_session_metadata = metadata
                self.recorded_frames = []
                self.is_recording = True
                
                # Update recording UI
                self.btn_rec.config(text="⏸ Pause")
                self.btn_stop.config(state="normal")   # Stop is now valid
                
                session_label = (
                    f"{metadata['session_id']}\n"
                    f"Patient: {metadata['patient_id']}\n"
                    f"PT: {metadata['pt_id']}\n"
                    f"{metadata['treatment_location_display']}"
                )
                self.lbl_rec.config(text=session_label, foreground="red")
                
                # Update DMR info bar
                self.dmr_session_widget.set_session(metadata)
                
                # Update status
                self.status_var.set(
                    f"📋 Recording DMR: {metadata['session_id']} - "
                    f"Patient {metadata['patient_id']} - PT {metadata['pt_id']}")
                
                print(f"\n{'='*60}")
                print(f"DMR SESSION STARTED")
                print(f"{'='*60}")
                print(f"Session ID: {metadata['session_id']}")
                print(f"Patient: {metadata['patient_id']}")
                print(f"Location: {metadata['treatment_location_display']}")
                print(f"PT: {metadata['pt_id']}")
                if metadata.get('pta_id'):
                    print(f"PTA: {metadata['pta_id']}")
                print(f"Type: {metadata['treatment_type_display']}")
                print(f"{'='*60}\n")
        
        # Open DMR session dialog - pass self (TactileSenseClinical) not self.root
        DMRSessionDialog(self, on_session_created)
    
    def stop_record(self):
        """Stop recording and save DMR — works from both RECORDING and PAUSED states"""
        # Nothing to stop if there is no active session at all
        if not self.current_session_metadata and not self.recorded_frames:
            messagebox.showwarning("Nothing to Stop",
                "No DMR session is active.\n\n"
                "Click ⏺ Record to start a new session first.")
            return
        
        # Stop the recording loop regardless of current state
        self.is_recording = False
        self.frame_capture_scheduled = False  # Stop frame capture
        self.pulse_buffer.clear()  # Clear accumulated pulses
        self.btn_rec.config(text="⏺ Record")
        self.btn_stop.config(state="disabled")
        self.lbl_rec.config(text="Click ⏺ Record to start a DMR session", foreground="gray")
        
        # If we have session data, prompt to save
        if self.current_session_metadata and self.recorded_frames:
            # Calculate duration from actual frame period (stored in first frame)
            if self.recorded_frames and 'frame_period_ms' in self.recorded_frames[0]:
                avg_frame_period_ms = np.mean([f.get('frame_period_ms', 50) for f in self.recorded_frames])
                duration = len(self.recorded_frames) * (avg_frame_period_ms / 1000.0)
            else:
                duration = len(self.recorded_frames) * 0.05  # Fallback to 50ms
            
            response = messagebox.askyesno("Save Digital Master Record?",
                f"DMR Session Complete\n\n"
                f"Session: {self.current_session_metadata['session_id']}\n"
                f"Patient: {self.current_session_metadata['patient_id']}\n"
                f"Location: {self.current_session_metadata['treatment_location_display']}\n"
                f"Frames: {len(self.recorded_frames)}\n"
                f"Duration: {duration:.1f} seconds\n\n"
                f"Save this Digital Master Record?")
            
            if response:
                self._save_dmr_file()
            else:
                # Discard
                self.current_session_metadata = None
                self.recorded_frames = []
                self.dmr_session_widget.clear_session()
                self.status_var.set("DMR session discarded")
        else:
            # Session metadata exists but zero frames were captured.
            # This usually means Stop was clicked immediately after Start.
            self.status_var.set("⚠ Session stopped — no sensor data recorded")
            messagebox.showwarning("No Data Captured",
                "The session was stopped before any sensor data was recorded.\n\n"
                "Make sure the sensor is connected (Sensor → Demo Simulator)\n"
                "and wait a few seconds after clicking Record before clicking Stop.\n\n"
                "Session metadata will be discarded.")
            self.current_session_metadata = None
            self.recorded_frames = []
            self.dmr_session_widget.clear_session()
    
    def _save_dmr_file(self):
        """Save complete DMR to file"""
        if not self.current_session_metadata:
            return
        
        meta = self.current_session_metadata
        
        # Suggest filename
        suggested = (
            f"DMR_{meta['patient_id']}_"
            f"{meta['treatment_location']}_"
            f"{meta['date'].replace('-', '')}.json"
        )
        
        # Pick the right sub-folder based on treatment type
        ttype = meta.get('treatment_type', 'pt_protocol')
        if ttype == 'pta_execution':
            save_dir = self._pta_dir()
        else:
            save_dir = self._pt_dir()   # default for pt_protocol & robot

        filename = filedialog.asksaveasfilename(
            title="Save Digital Master Record",
            initialdir=save_dir,
            initialfile=suggested,
            defaultextension=".json",
            filetypes=[
                ("Digital Master Record (JSON)", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            # Build complete DMR document
            dmr_document = {
                'dmr_format_version': '1.0',
                'created_by': 'TactileSense v3.2 DMR Edition',
                'device': 'PT Robotic Therapeutic System',
                'session': self.current_session_metadata,
                'pressure_zones': self.pressure_zones,
                'frames': self.recorded_frames,
                'summary': {
                    'total_frames': len(self.recorded_frames),
                    'duration_seconds': len(self.recorded_frames) * 0.05,
                    'recording_complete': True
                }
            }
            
            # Save to JSON
            try:
                with open(filename, 'w') as f:
                    json.dump(dmr_document, f, indent=2)
                
                self.status_var.set(f"✓ DMR saved: {filename}")
                
                # Check if we should auto-export CSV
                csv_exported = False
                csv_filename = None
                if meta.get('auto_export_csv', False):
                    csv_filename = self._auto_export_csv(meta)
                    csv_exported = (csv_filename is not None)
                
                # Build confirmation message
                if csv_exported:
                    message = (
                        f"DMR saved successfully!\n\n"
                        f"DMR File: {filename}\n"
                        f"CSV File: {csv_filename}\n\n"
                        f"Session: {meta['session_id']}\n"
                        f"Patient: {meta['patient_id']}\n"
                        f"Frames: {len(self.recorded_frames)}\n"
                        f"Duration: {len(self.recorded_frames) * 0.05:.1f}s\n\n"
                        f"─────────────────────────────────\n"
                        f"✓ CSV auto-exported to CSV_Exports folder\n"
                        f"Data is still loaded. You can:\n"
                        f"  • DMR → Export Report (statistics)\n"
                        f"Data clears when you start a new session."
                    )
                else:
                    message = (
                        f"DMR saved successfully!\n\n"
                        f"File: {filename}\n"
                        f"Session: {meta['session_id']}\n"
                        f"Patient: {meta['patient_id']}\n"
                        f"Frames: {len(self.recorded_frames)}\n"
                        f"Duration: {len(self.recorded_frames) * 0.05:.1f}s\n\n"
                        f"─────────────────────────────────\n"
                        f"Data is still loaded.  You can still:\n"
                        f"  • File → Export Data  (CSV)\n"
                        f"  • DMR  → Export Report\n"
                        f"Data clears when you start a new session."
                    )
                
                messagebox.showinfo("Digital Master Record Saved", message)
                
                print(f"\n{'='*60}")
                print(f"DMR SAVED SUCCESSFULLY")
                print(f"{'='*60}")
                print(f"File: {filename}")
                print(f"Frames: {len(self.recorded_frames)}")
                if csv_exported:
                    print(f"CSV auto-exported: {csv_filename}")
                print(f"{'='*60}\n")
                
                # Keep frames and metadata loaded — user may still want to
                # export CSV (File → Export Data) or a report (DMR → Export Report).
                # Data clears automatically when a new session starts.
                self._session_saved = True
                
                # Update status message based on whether CSV was auto-exported
                if meta.get('auto_export_csv', False):
                    self.status_var.set(
                        f"✓ DMR & CSV saved.  Report: DMR → Export Report")
                else:
                    self.status_var.set(
                        f"✓ DMR saved.  Export CSV: File → Export Data  |  Report: DMR → Export Report")
                
            except Exception as e:
                messagebox.showerror("Save Error",
                    f"Error saving DMR file:\n{str(e)}")
                print(f"Error saving DMR: {e}")
    
    def _auto_export_csv(self, meta):
        """
        Automatically export CSV file when DMR is saved (if auto_export_csv was enabled).
        Returns the filename if successful, None otherwise.
        """
        if not self.recorded_frames:
            return None
        
        # Pick the right CSV directory based on treatment type
        ttype = meta.get('treatment_type', 'pt_protocol')
        if ttype == 'pta_execution':
            csv_dir = self._pta_csv_dir()
        elif ttype == 'robot_execution':
            csv_dir = self._robot_csv_dir()
        else:
            csv_dir = self._pt_csv_dir()
        
        # Auto-generate filename (no dialog)
        csv_filename = os.path.join(
            csv_dir,
            f"CSV_{meta['patient_id']}_"
            f"{meta['treatment_location']}_"
            f"{meta['date'].replace('-', '')}_"
            f"{meta['time'].replace(':', '')}.csv"
        )
        
        try:
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header row
                header = ["Frame", "Timestamp", "Pattern", "Roll", "Pitch", "Yaw"]
                header += [f"Sensor_{i}" for i in range(65)]
                writer.writerow(header)
                
                # Data rows
                for frame in self.recorded_frames:
                    row = [
                        frame.get('frame_number', ''),
                        frame.get('timestamp', ''),
                        frame.get('demo_pattern', ''),
                        frame.get('hand_orientation', {}).get('roll', 0),
                        frame.get('hand_orientation', {}).get('pitch', 0),
                        frame.get('hand_orientation', {}).get('yaw', 0),
                    ]
                    row += frame.get('sensor_data', [0]*65)
                    writer.writerow(row)
            
            return csv_filename
        
        except Exception as e:
            print(f"⚠ Auto-export CSV failed: {e}")
            return None
    

    
    # ========================================================================
    # DMR UTILITY METHODS - NEW in v3.2
    # ========================================================================
    
    def view_session_info(self):
        """View detailed current DMR session information"""
        if not self.current_session_metadata:
            messagebox.showinfo("No Active DMR Session",
                "No DMR session is currently active.\n\n"
                "Click ⏺ Record to start a new Digital Master Record session.")
            return
        
        m = self.current_session_metadata
        
        info_text = (
            f"DIGITAL MASTER RECORD\n"
            f"Current Session Details\n"
            f"{'-'*50}\n\n"
            f"Session ID: {m['session_id']}\n"
            f"Date: {m['date']}\n"
            f"Time Started: {m['time']}\n\n"
            f"PATIENT:\n"
            f"  ID: {m['patient_id']}\n\n"
            f"TREATMENT:\n"
            f"  Location: {m['treatment_location_display']}\n"
            f"  Type: {m['treatment_type_display']}\n\n"
            f"PRACTITIONERS:\n"
            f"  Physical Therapist: {m['pt_id']}\n"
        )
        
        if m.get('pta_id'):
            info_text += f"  PT Assistant: {m['pta_id']}\n"
        
        if m.get('notes'):
            info_text += f"\nNOTES:\n{m['notes']}\n"
        
        info_text += (
            f"\nRECORDING STATUS:\n"
            f"  Frames Captured: {len(self.recorded_frames)}\n"
            f"  Duration: {len(self.recorded_frames) * 0.05:.1f} seconds\n"
            f"  Recording: {'Yes' if self.is_recording else 'Paused'}"
        )
        
        messagebox.showinfo("DMR Session Information", info_text)
    
    def view_frames(self):
        """Open frame viewer for clinical review of recorded frames"""
        print(f"\n=== VIEW FRAMES DEBUG ===")
        print(f"recorded_frames count: {len(self.recorded_frames)}")
        print(f"is_recording: {self.is_recording}")
        print(f"current_session_metadata exists: {self.current_session_metadata is not None}")
        
        if not self.recorded_frames:
            if self.is_recording and self.current_session_metadata:
                messagebox.showwarning("No Frames Yet",
                    "Recording is active but no frames have been captured yet.\n\n"
                    "Wait a few seconds for frames to accumulate,\n"
                    "then open the Frame Viewer.")
            else:
                messagebox.showwarning("No Frames to Review",
                    "No recorded frames available.\n\n"
                    "To review frames:\n"
                    "1. Record a DMR session, or\n"
                    "2. Load a previous DMR file (DMR → Load Previous DMR)\n\n"
                    "Then use DMR → Review Frames.")
            return
        
        # Debug: Show first frame structure
        if self.recorded_frames:
            print(f"First frame keys: {self.recorded_frames[0].keys()}")
            print(f"First frame sensor_data type: {type(self.recorded_frames[0].get('sensor_data'))}")
            if self.recorded_frames[0].get('sensor_data'):
                print(f"First frame sensor_data length: {len(self.recorded_frames[0].get('sensor_data'))}")
                print(f"First frame sensor_data sample: {self.recorded_frames[0].get('sensor_data')[:5]}")
        
        # Open the frame viewer
        print(f"Opening FrameViewer with {len(self.recorded_frames)} frames")
        FrameViewer(self.root, self.recorded_frames, self.pressure_zones,
                   self.current_session_metadata)
    
    def load_dmr(self):
        """Load a previous DMR file — puts frames and metadata into memory so export works."""
        filename = filedialog.askopenfilename(
            title="Load Digital Master Record",
            filetypes=[
                ("Digital Master Record (JSON)", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    dmr_data = json.load(f)
                
                session = dmr_data.get('session', {})
                frames  = dmr_data.get('frames', [])
                summary = dmr_data.get('summary', {})
                
                # ---- populate in-memory state ----
                self.current_session_metadata = session
                self.recorded_frames         = frames
                self.is_recording            = False
                self._session_saved          = True   # treat like a saved session; next Record = new
                self.dmr_session_widget.set_session(session)
                self.btn_rec.config(text="⏺ Record")
                self.lbl_rec.config(
                    text=f"{session.get('session_id','')}\n"
                         f"Patient: {session.get('patient_id','')}\n"
                         f"{session.get('treatment_location_display','')}",
                    foreground="darkblue")

                info = (
                    f"DMR Loaded — ready to export!\n\n"
                    f"Session : {session.get('session_id', 'Unknown')}\n"
                    f"Patient : {session.get('patient_id', 'Unknown')}\n"
                    f"Location: {session.get('treatment_location_display', 'Unknown')}\n"
                    f"PT      : {session.get('pt_id', 'Unknown')}\n"
                    f"Date    : {session.get('date', 'Unknown')}\n\n"
                    f"Frames  : {len(frames)}\n"
                    f"Duration: {summary.get('duration_seconds', 0):.1f}s\n\n"
                    f"You can now:\n"
                    f"  • File → Export Data   (CSV)\n"
                    f"  • DMR  → Export Report (CSV)\n"
                    f"Pressing Record will start a new session."
                )
                
                messagebox.showinfo("DMR Loaded", info)
                self.status_var.set(
                    f"✓ DMR loaded: {len(frames)} frames — "
                    f"File → Export Data  |  DMR → Export Report")
                
                print(f"✓ DMR loaded: {filename}  ({len(frames)} frames into memory)")

            except Exception as e:
                messagebox.showerror("Load Error",
                    f"Error loading DMR file:\n{str(e)}")
    
    def export_dmr_report(self):
        """Export a human-readable CSV report of the current DMR session."""
        if not self.current_session_metadata:
            messagebox.showwarning("No Active Session",
                "No DMR session to export.\n\n"
                "To create a report:\n"
                "1. Record a DMR session, or\n"
                "2. Load a previous DMR file (DMR → Load Previous DMR)\n\n"
                "Then use DMR → Export Report.")
            return

        if not self.recorded_frames:
            if self.is_recording:
                # Recording active but no frames yet
                messagebox.showwarning("No Frames Yet",
                    "Recording is active but no frames have been captured yet.\n\n"
                    "Wait a few seconds for frames to accumulate,\n"
                    "then try exporting the report.")
            else:
                # Session exists but no frames (stopped too soon)
                messagebox.showwarning("No Frames to Report",
                    "This session has no recorded frames.\n\n"
                    "The session was stopped before any sensor data was captured.\n"
                    "Start a new recording and wait for frames to accumulate.")
            return

        meta = self.current_session_metadata
        suggested = f"Report_{meta['patient_id']}_{meta['date'].replace('-','')}.csv"

        filename = filedialog.asksaveasfilename(
            title="Export DMR Report",
            initialdir=self._get_default_dir(),
            initialfile=suggested,
            defaultextension=".csv",
            filetypes=[("CSV Report", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return

        try:
            # Pre-compute per-frame summaries
            zones = self.pressure_zones
            rows = []
            for frame in self.recorded_frames:
                sd = frame.get('sensor_data', [])
                if sd:
                    active = [v for v in sd if v > 1.0]
                    peak  = max(sd)
                    avg   = sum(active)/len(active) if active else 0.0
                    # zone classification of average
                    if avg < zones['therapeutic_min']:
                        zone = "Below Therapeutic"
                    elif avg <= zones['therapeutic_max']:
                        zone = "Therapeutic OK"
                    elif avg <= zones['caution_max']:
                        zone = "Above Therapeutic"
                    else:
                        zone = "CAUTION"
                else:
                    peak = avg = 0.0
                    zone = "No Data"
                rows.append((frame.get('frame_number',0),
                             frame.get('timestamp',''),
                             frame.get('demo_pattern',''),
                             f"{peak:.2f}",
                             f"{avg:.2f}",
                             zone,
                             len([v for v in sd if v > 1.0]) if sd else 0))

            with open(filename, 'w', newline='') as f:
                w = csv.writer(f)
                # ---- metadata block (first rows, no table structure) ----
                w.writerow(["DMR CLINICAL REPORT"])
                w.writerow(["Generated", datetime.now().isoformat()])
                w.writerow(["Session ID",  meta.get('session_id','')])
                w.writerow(["Patient",     meta.get('patient_id','')])
                w.writerow(["Location",    meta.get('treatment_location_display','')])
                w.writerow(["PT",          meta.get('pt_id','')])
                w.writerow(["PTA",         meta.get('pta_id','')])
                w.writerow(["Type",        meta.get('treatment_type_display','')])
                w.writerow(["Notes",       meta.get('notes','')])
                w.writerow(["Zones",
                            f"Min={zones['therapeutic_min']:.0f}",
                            f"Max={zones['therapeutic_max']:.0f}",
                            f"Caut={zones['caution_max']:.0f}"])
                w.writerow([])  # blank separator
                # ---- per-frame summary table ----
                w.writerow(["Frame","Timestamp","Pattern",
                            "Peak_kPa","Avg_kPa","Zone","Active_Sensors"])
                w.writerows(rows)

            # summary stats for popup
            peaks = [float(r[3]) for r in rows]
            avgs  = [float(r[4]) for r in rows]
            dur   = len(self.recorded_frames) * 0.05

            messagebox.showinfo("DMR Report Exported",
                f"Report saved!\n\n"
                f"File     : {filename}\n"
                f"Frames   : {len(self.recorded_frames)}\n"
                f"Duration : {dur:.1f} s\n"
                f"Peak max : {max(peaks):.1f} kPa\n"
                f"Avg mean : {sum(avgs)/len(avgs):.1f} kPa\n\n"
                f"Open with Excel for full analysis.")
            self.status_var.set(f"✓ Report exported: {filename}")
            print(f"✓ Report exported: {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Could not write file:\n\n{e}")
            print(f"Report export error: {e}")
    
    def show_about_dmr(self):
        """Show detailed information about Digital Master Record"""
        messagebox.showinfo("About Digital Master Record (DMR)",
            "DIGITAL MASTER RECORD (DMR)\n"
            "Patent-Pending Methodology\n"
            "PT Robotic Therapeutic System\n\n"
            "═══════════════════════════════════\n\n"
            "What is a DMR?\n\n"
            "The Digital Master Record captures complete\n"
            "treatment data for FDA-compliant documentation:\n\n"
            "✓ Patient identification\n"
            "✓ PT/PTA practitioner IDs\n"
            "✓ Treatment location (body part)\n"
            "✓ Complete pressure data (65 sensors)\n"
            "✓ Hand orientation (3D space)\n"
            "✓ Time-stamped frames (50ms resolution)\n"
            "✓ Pressure zone compliance\n"
            "✓ Clinical notes\n\n"
            "═══════════════════════════════════\n\n"
            "Three Use Cases:\n\n"
            "1. PT PROTOCOL DEVELOPMENT\n"
            "   Licensed PT treats patient while system\n"
            "   captures expert technique as DMR.\n\n"
            "2. PTA EXECUTION\n"
            "   PT Assistant follows PT-created DMR.\n"
            "   System monitors compliance.\n\n"
            "3. ROBOT AUTONOMOUS EXECUTION\n"
            "   Robot loads DMR and replicates exactly.\n"
            "   System ensures safety.\n\n"
            "═══════════════════════════════════\n\n"
            "© 2025 PT Robotic LLC\n"
            "Patent Pending")
    
    def save_session(self):
        """Save current session (metadata + frames) as a JSON file."""
        # Warn if no frames
        if not self.recorded_frames:
            if self.is_recording and self.current_session_metadata:
                response = messagebox.askyesno("No Frames Yet",
                    "Recording is active but no frames have been captured yet.\n\n"
                    "The saved file will contain session info but no sensor data.\n\n"
                    "Do you want to save anyway?\n"
                    "(Recommended: Wait for frames, then click ⏹ Stop & Save instead)")
                if not response:
                    return
            elif not self.current_session_metadata:
                messagebox.showwarning("No Session to Save",
                    "No DMR session is active.\n\n"
                    "Click ⏺ Record to start a session first.")
                return
        
        # Build whatever we have — even if only metadata
        payload = {
            'saved_by': 'TactileSense v3.2 (File → Save Session)',
            'timestamp': datetime.now().isoformat(),
            'session': self.current_session_metadata,
            'pressure_zones': self.pressure_zones,
            'frames': self.recorded_frames,
            'frame_count': len(self.recorded_frames),
        }

        filename = filedialog.asksaveasfilename(
            title="Save Session",
            initialdir=self._get_default_dir(),
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                json.dump(payload, f, indent=2)

            messagebox.showinfo("Session Saved",
                f"Saved successfully!\n\n"
                f"File   : {filename}\n"
                f"Frames : {len(self.recorded_frames)}")
            self.status_var.set(f"✓ Session saved: {filename}")
            print(f"✓ Session saved: {filename}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Could not write file:\n\n{e}")
            print(f"Save error: {e}")
    
    def export_data(self):
        """Export current recorded frames to a real CSV file."""
        # Nothing to export?
        if not self.recorded_frames:
            # Give specific guidance based on current state
            if self.is_recording and self.current_session_metadata:
                # Recording is active but no frames yet (clicked export too soon)
                messagebox.showwarning("No Frames Captured Yet",
                    "Recording is active but no frames have been captured yet.\n\n"
                    "Wait a few seconds for frames to accumulate,\n"
                    "then try exporting again.\n\n"
                    "Current status: Recording in progress...")
            elif self.current_session_metadata and not self.is_recording:
                # Session exists but recording paused/stopped with 0 frames
                messagebox.showwarning("No Frames Recorded",
                    "This session was stopped before any frames were captured.\n\n"
                    "Make sure the sensor is connected and wait a few seconds\n"
                    "after clicking Record before clicking Stop.\n\n"
                    "Start a new session to record frames.")
            else:
                # No session at all
                messagebox.showwarning("Nothing to Export",
                    "No recorded frames available.\n\n"
                    "To export sensor data:\n"
                    "1. Connect sensor (Sensor → Demo Simulator)\n"
                    "2. Click ⏺ Record and fill in patient info\n"
                    "3. Wait for frames to accumulate\n"
                    "4. Click ⏹ Stop & Save\n"
                    "5. Then export data\n\n"
                    "Or load a previous DMR file first.")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Sensor Data as CSV",
            initialdir=self._get_default_dir(),
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return                          # user cancelled

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Header row
                header = ["Frame", "Timestamp", "Pattern",
                          "Roll", "Pitch", "Yaw"]
                header += [f"Sensor_{i}" for i in range(65)]
                writer.writerow(header)

                # Data rows
                for frame in self.recorded_frames:
                    row = [
                        frame.get('frame_number', ''),
                        frame.get('timestamp', ''),
                        frame.get('demo_pattern', ''),
                        frame.get('hand_orientation', {}).get('roll', 0),
                        frame.get('hand_orientation', {}).get('pitch', 0),
                        frame.get('hand_orientation', {}).get('yaw', 0),
                    ]
                    row += frame.get('sensor_data', [0]*65)
                    writer.writerow(row)

            messagebox.showinfo("CSV Exported",
                f"Exported successfully!\n\n"
                f"File : {filename}\n"
                f"Rows : {len(self.recorded_frames)}\n"
                f"Cols : 71  (6 meta + 65 sensors)\n\n"
                f"Open with Excel or any spreadsheet app.")
            self.status_var.set(f"✓ CSV exported: {filename}")
            print(f"✓ CSV exported: {filename}  ({len(self.recorded_frames)} rows)")

        except Exception as e:
            messagebox.showerror("Export Error", f"Could not write file:\n\n{e}")
            print(f"Export error: {e}")
    
    def show_about(self):
        """About - same as v3.0 but updated"""
        messagebox.showinfo("About",
            "TactileSense v3.1\n"
            "Digital Master Record (DMR) Edition\n\n"
            "NEW in v3.1:\n"
            "• Interactive sliders for zones\n"
            "• LIVE visual preview\n"
            "• See colors change in real-time!\n"
            "• Quick presets\n\n"
            "All v3.0 features included:\n"
            "• PT pressure zones\n"
            "• 3D hand orientation\n"
            "• Clinical monitoring\n\n"
            "© 2025 PT Robotic LLC")

def main():
    """Main entry point for TactileSense v3.2 DMR Edition"""
    print("="*70)
    print("TactileSense v3.2 - DIGITAL MASTER RECORD (DMR) EDITION")
    print("="*70)
    print()
    print("Complete Clinical Documentation System")
    print()
    print("NEW in v3.2:")
    print("  ✓ Digital Master Record (DMR) session metadata")
    print("  ✓ Patient ID tracking")
    print("  ✓ PT and PTA practitioner identification")
    print("  ✓ Treatment location selection")
    print("  ✓ Automatic date/time capture")
    print("  ✓ FDA-compliant audit trail")
    print("  ✓ Complete session save/load")
    print()
    print("v3.1 features included:")
    print("  ✓ Interactive zone configuration")
    print("  ✓ Live visual feedback")
    print()
    print("v3.0 features included:")
    print("  ✓ PT-defined pressure zones")
    print("  ✓ 3D hand orientation display")
    print()
    print("HOW TO USE:")
    print("  1. Select: Sensor → Demo Simulator or TactileGlove")
    print("  2. Click: ⏺ Record")
    print("  3. Enter: Patient ID, PT ID, Treatment location")
    print("  4. Record: Treatment session")
    print("  5. Stop & Save: Complete Digital Master Record!")
    print()
    print("="*70)
    print()
    
    try:
        root = tk.Tk()
        app = TactileSenseClinical(root)
        print("✓ TactileSense v3.2 DMR Edition ready!")
        print("✓ Click ⏺ Record to create your first DMR!")
        print()
        root.mainloop()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
