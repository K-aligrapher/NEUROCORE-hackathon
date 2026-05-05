#!/usr/bin/env python3
"""
Thalassemia Data Preprocessing Script
Extracts and organizes zip files into binary classification (Normal vs Abnormal)
"""

import zipfile
import shutil
from pathlib import Path
from typing import Dict, List
import json


class ThalassemiaDataPreprocessor:
    """Preprocess thalassemia dataset"""
    
    def __init__(self, zip_dir: str):
        self.zip_dir = Path(zip_dir)
        self.output_dir = Path("data")
        
        # Binary classification mapping
        self.classification = {
            "normal": ["4 normal 1426"],
            "abnormal": [
                "1 Elliptocyte 1211",
                "2 pencil 24",
                "3 teardrop 2076",
                "5 stomatocyte 382",
                "6 TARGETSEL 851",
                "7 hypochromic 222",
                "8 SPERO bulat 562",
                "9 acantocyte 354"
            ]
        }
        
        self.stats = {
            "total_extracted": 0,
            "normal_count": 0,
            "abnormal_count": 0,
            "failed": []
        }
    
    def extract_zip_files(self):
        """Extract all zip files"""
        print("=" * 60)
        print("Extracting zip files...")
        print("=" * 60)
        
        zip_files = sorted(self.zip_dir.glob("*.zip"))
        print(f"Found {len(zip_files)} zip files\n")
        
        for zip_file in zip_files:
            try:
                print(f"Extracting: {zip_file.name}")
                
                # Create temp extraction folder
                extract_folder = self.zip_dir / zip_file.stem
                extract_folder.mkdir(exist_ok=True)
                
                # Extract
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
                
                print(f"  ✓ Extracted to {extract_folder.name}\n")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}\n")
                self.stats["failed"].append(zip_file.name)
    
    def organize_by_classification(self):
        """Organize extracted files into binary class folders"""
        print("=" * 60)
        print("Organizing files into binary classification...")
        print("=" * 60)
        
        # Create output directories
        normal_dir = self.output_dir / "normal"
        abnormal_dir = self.output_dir / "abnormal"
        
        normal_dir.mkdir(parents=True, exist_ok=True)
        abnormal_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nOutput directories:")
        print(f"  Normal: {normal_dir}")
        print(f"  Abnormal: {abnormal_dir}\n")
        
        # Process normal images
        for cell_type in self.classification["normal"]:
            self._copy_images(cell_type, normal_dir, "normal")
        
        # Process abnormal images
        for cell_type in self.classification["abnormal"]:
            self._copy_images(cell_type, abnormal_dir, "abnormal")
    
    def _copy_images(self, cell_type: str, target_dir: Path, label: str):
        """Copy images from cell type folder to target classification folder"""
        
        # Find the extracted folder
        source_dirs = list(self.zip_dir.glob(f"*{cell_type}*"))
        
        if not source_dirs:
            print(f"  ✗ Not found: {cell_type}")
            self.stats["failed"].append(cell_type)
            return
        
        source_dir = source_dirs[0]
        
        # Find the actual data folder (might be nested)
        data_folders = []
        for item in source_dir.rglob("*"):
            if item.is_dir() and any(item.glob("*.png")) or any(item.glob("*.jpg")):
                data_folders.append(item)
        
        if not data_folders:
            data_folders = [source_dir]
        
        # Copy all images
        image_count = 0
        for data_folder in data_folders:
            for img_file in data_folder.glob("*.png"):
                try:
                    shutil.copy2(img_file, target_dir / img_file.name)
                    image_count += 1
                except Exception as e:
                    print(f"    Error copying {img_file.name}: {e}")
            
            for img_file in data_folder.glob("*.jpg"):
                try:
                    shutil.copy2(img_file, target_dir / img_file.name)
                    image_count += 1
                except Exception as e:
                    print(f"    Error copying {img_file.name}: {e}")
        
        if label == "normal":
            self.stats["normal_count"] += image_count
        else:
            self.stats["abnormal_count"] += image_count
        
        print(f"  ✓ {cell_type}: {image_count} images → {label}/")
    
    def save_statistics(self):
        """Save preprocessing statistics"""
        stats_file = self.output_dir / "preprocessing_stats.json"
        
        stats_data = {
            "normal_samples": self.stats["normal_count"],
            "abnormal_samples": self.stats["abnormal_count"],
            "total_samples": self.stats["normal_count"] + self.stats["abnormal_count"],
            "failed": self.stats["failed"],
            "classification_mapping": self.classification
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        return stats_data
    
    def print_summary(self, stats: Dict):
        """Print preprocessing summary"""
        print("\n" + "=" * 60)
        print("PREPROCESSING SUMMARY")
        print("=" * 60)
        print(f"Normal samples:    {stats['normal_samples']:,}")
        print(f"Abnormal samples:  {stats['abnormal_samples']:,}")
        print(f"Total samples:     {stats['total_samples']:,}")
        print(f"Failed:            {len(stats['failed'])}")
        print(f"\nOutput directory:  {self.output_dir}")
        print("=" * 60 + "\n")
    
    def cleanup_extractions(self):
        """Clean up temporary extraction folders (optional)"""
        print("Cleaning up temporary extraction folders...")
        for extracted_dir in self.zip_dir.glob("*"):
            if extracted_dir.is_dir() and not extracted_dir.name.startswith("data"):
                try:
                    shutil.rmtree(extracted_dir)
                    print(f"  ✓ Removed {extracted_dir.name}")
                except Exception as e:
                    print(f"  ✗ Failed to remove {extracted_dir.name}: {e}")
    
    def run(self, cleanup: bool = True):
        """Run full preprocessing pipeline"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║  THALASSEMIA BINARY CLASSIFICATION DATA PREPROCESSING  ║")
        print("╚" + "=" * 58 + "╝")
        print("\n")
        
        # Step 1: Extract
        self.extract_zip_files()
        
        # Step 2: Organize
        self.organize_by_classification()
        
        # Step 3: Save stats
        stats = self.save_statistics()
        
        # Step 4: Print summary
        self.print_summary(stats)
        
        # Step 5: Cleanup
        if cleanup:
            self.cleanup_extractions()
        
        print("✓ Preprocessing complete!")
        print(f"✓ Ready to train! Use data/ folder for training.\n")


def main():
    """Main entry point"""
    # Point to the zip files directory
    zip_directory = "rfdz6wfzn4-1/rfdz6wfzn4-1"
    
    preprocessor = ThalassemiaDataPreprocessor(zip_directory)
    preprocessor.run(cleanup=True)


if __name__ == "__main__":
    main()
