#!/usr/bin/env python3
"""
Enhanced Map Visualization Module for ForenGeo
Provides advanced mapping capabilities with heatmaps, hexagons, and clustering
"""

import folium
from folium import plugins
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import h3

class MapVisualizer:
    """Advanced map visualization with H3 hexagons, heatmaps, and clustering"""

    def __init__(self, center_lat: float = 40.7128, center_lon: float = -74.0060, zoom_start: int = 10):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.zoom_start = zoom_start

    def create_heatmap(self, locations_df: pd.DataFrame, output_file: str = 'heatmap.html') -> str:
        """Create heatmap visualization of location density"""
        if locations_df.empty:
            print("⚠️ No location data for heatmap")
            return None

        # Calculate center from data
        center_lat = locations_df['lat'].mean()
        center_lon = locations_df['lon'].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )

        # Prepare data for heatmap
        heat_data = locations_df[['lat', 'lon']].values.tolist()

        # Add heatmap layer
        plugins.HeatMap(
            heat_data,
            name='Density Heatmap',
            radius=15,
            blur=25,
            max_zoom=1,
            show=True
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        m.save(output_file)
        print(f"🔥 Heatmap saved to {output_file}")
        return output_file

    def create_hexagon_map(self, h3_hexagons: Dict[str, int], output_file: str = 'hexagons.html',
                          resolution: int = 9) -> str:
        """Create map with H3 hexagon visualization"""
        if not h3_hexagons:
            print("⚠️ No hexagon data")
            return None

        # Get center from hexagons
        hex_list = list(h3_hexagons.keys())
        boundaries = [h3.h3_to_geo_boundary(h) for h in hex_list[:1]]
        center = h3.h3_to_geo(hex_list[0])

        m = folium.Map(
            location=center,
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )

        # Find max count for color scaling
        max_count = max(h3_hexagons.values()) if h3_hexagons else 1

        # Add hexagons
        for hex_id, count in h3_hexagons.items():
            boundary = h3.h3_to_geo_boundary(hex_id)
            
            # Color intensity based on visit count
            intensity = count / max_count
            color = self._get_color_for_intensity(intensity)
            
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in boundary],
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.5 + (0.4 * intensity),
                weight=2,
                popup=f"H3 Index: {hex_id}<br>Visits: {count}",
                tooltip=f"Visits: {count}"
            ).add_to(m)

        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"🔷 Hexagon map saved to {output_file}")
        return output_file

    def create_cluster_map(self, locations_df: pd.DataFrame, output_file: str = 'clusters.html') -> str:
        """Create clustered marker map"""
        if locations_df.empty:
            print("⚠️ No location data for clustering")
            return None

        center_lat = locations_df['lat'].mean()
        center_lon = locations_df['lon'].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )

        # Add clustered markers
        marker_cluster = plugins.MarkerCluster().add_to(m)

        for _, row in locations_df.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"Device: {row['device_id']}<br>Time: {row['timestamp']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"📍 Cluster map saved to {output_file}")
        return output_file

    def create_multi_layer_map(self, locations_df: pd.DataFrame, h3_hexagons: Dict[str, int] = None,
                              output_file: str = 'multi_layer.html') -> str:
        """Create map with multiple visualization layers"""
        if locations_df.empty:
            print("⚠️ No location data")
            return None

        center_lat = locations_df['lat'].mean()
        center_lon = locations_df['lon'].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )

        # Layer 1: Heatmap
        heat_data = locations_df[['lat', 'lon']].values.tolist()
        plugins.HeatMap(
            heat_data,
            name='Density Heatmap',
            radius=15,
            blur=25,
            show=False
        ).add_to(m)

        # Layer 2: Markers with clustering
        marker_cluster = plugins.MarkerCluster(name='Location Markers').add_to(m)
        for _, row in locations_df.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"Device: {row['device_id']}<br>Time: {row['timestamp']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

        # Layer 3: H3 Hexagons
        if h3_hexagons:
            hex_group = folium.FeatureGroup(name='H3 Hotspots', show=True)
            max_count = max(h3_hexagons.values())
            
            for hex_id, count in h3_hexagons.items():
                boundary = h3.h3_to_geo_boundary(hex_id)
                intensity = count / max_count
                color = self._get_color_for_intensity(intensity)
                
                folium.Polygon(
                    locations=[(lat, lon) for lon, lat in boundary],
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.4 + (0.3 * intensity),
                    weight=1,
                    popup=f"Visits: {count}"
                ).add_to(hex_group)
            
            hex_group.add_to(m)

        # Layer 4: Timeline (if timestamp available)
        if 'timestamp' in locations_df.columns:
            time_group = folium.FeatureGroup(name='Timeline', show=False)
            for idx, (_, row) in enumerate(locations_df.iterrows()):
                color = self._get_color_for_time_progression(idx, len(locations_df))
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=3,
                    color=color,
                    fill=True,
                    fill_color=color,
                    opacity=0.7,
                    popup=f"#{idx}: {row['timestamp']}"
                ).add_to(time_group)
            time_group.add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"🗺️ Multi-layer map saved to {output_file}")
        return output_file

    def create_trajectory_map(self, locations_df: pd.DataFrame, output_file: str = 'trajectory.html') -> str:
        """Create map showing movement trajectory"""
        if locations_df.empty:
            print("⚠️ No location data for trajectory")
            return None

        # Sort by timestamp
        df_sorted = locations_df.sort_values('timestamp')
        
        center_lat = df_sorted['lat'].mean()
        center_lon = df_sorted['lon'].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )

        # Draw trajectory line
        coordinates = [[row['lat'], row['lon']] for _, row in df_sorted.iterrows()]
        
        if len(coordinates) > 1:
            folium.PolyLine(
                coordinates,
                color='red',
                weight=2,
                opacity=0.8,
                popup='Movement Trajectory'
            ).add_to(m)

        # Add start and end markers
        if len(coordinates) > 0:
            folium.Marker(
                location=coordinates[0],
                popup='Start',
                icon=folium.Icon(color='green', icon='play')
            ).add_to(m)
            
            folium.Marker(
                location=coordinates[-1],
                popup='End',
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(m)

        # Add intermediate points
        for idx, coord in enumerate(coordinates[1:-1], 1):
            folium.CircleMarker(
                location=coord,
                radius=3,
                color='blue',
                fill=True,
                popup=f"Point #{idx}"
            ).add_to(m)

        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"📈 Trajectory map saved to {output_file}")
        return output_file

    def create_comparison_map(self, devices_data: Dict[str, pd.DataFrame], 
                             output_file: str = 'comparison.html') -> str:
        """Create comparison map for multiple devices"""
        if not devices_data:
            print("⚠️ No device data for comparison")
            return None

        # Get center from all data
        all_lats = []
        all_lons = []
        for df in devices_data.values():
            all_lats.extend(df['lat'].tolist())
            all_lons.extend(df['lon'].tolist())

        center_lat = sum(all_lats) / len(all_lats) if all_lats else 0
        center_lon = sum(all_lons) / len(all_lons) if all_lons else 0

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )

        colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen']
        
        for (device_id, df), color in zip(devices_data.items(), colors):
            feature_group = folium.FeatureGroup(name=f'Device: {device_id}')
            
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=4,
                    color=color,
                    fill=True,
                    fill_color=color,
                    popup=f"Device: {device_id}<br>Time: {row['timestamp']}"
                ).add_to(feature_group)
            
            feature_group.add_to(m)

        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"🔀 Comparison map saved to {output_file}")
        return output_file

    def create_entity_map(self, entities_df: pd.DataFrame, output_file: str = 'entity_map.html') -> str:
        """Create map for geolocated OSINT entities."""
        if entities_df.empty:
            print("⚠️ No geolocated OSINT entities")
            return None

        center_lat = entities_df['lat'].mean()
        center_lon = entities_df['lon'].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start,
            tiles='Stamen Toner'
        )

        entity_group = folium.FeatureGroup(name='OSINT Entities')
        for _, row in entities_df.iterrows():
            color = 'blue' if row['type'] == 'ips' else 'purple' if row['type'] == 'domains' else 'green'
            popup = f"Type: {row['type']}<br>Value: {row['value']}"
            if row['metadata']:
                popup += f"<br>Details: {json.dumps(row['metadata'], ensure_ascii=False)[:200]}"
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                popup=popup,
                tooltip=row['value']
            ).add_to(entity_group)

        entity_group.add_to(m)
        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"🧭 Entity map saved to {output_file}")
        return output_file

    @staticmethod
    def _get_color_for_intensity(intensity: float) -> str:
        """Get color based on intensity (0-1)"""
        if intensity < 0.2:
            return '#FFFF00'  # Yellow
        elif intensity < 0.4:
            return '#FFA500'  # Orange
        elif intensity < 0.6:
            return '#FF6347'  # Tomato
        elif intensity < 0.8:
            return '#FF4500'  # OrangeRed
        else:
            return '#DC143C'  # Crimson

    @staticmethod
    def _get_color_for_time_progression(current_idx: int, total_count: int) -> str:
        """Get color based on time progression"""
        progress = current_idx / (total_count - 1) if total_count > 1 else 0
        
        if progress < 0.25:
            return '#0000FF'  # Blue
        elif progress < 0.5:
            return '#00FFFF'  # Cyan
        elif progress < 0.75:
            return '#00FF00'  # Green
        elif progress < 0.9:
            return '#FFFF00'  # Yellow
        else:
            return '#FF0000'  # Red
