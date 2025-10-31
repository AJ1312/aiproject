#!/usr/bin/env python3
"""
Academic Performance ML Analyzer
Uses actual Machine Learning algorithms (not API-based AI) to analyze VTOP data
- Clustering: Groups similar courses using KMeans
- Regression: Predicts final grades using LinearRegression
- Pattern Recognition: Identifies performance patterns across semesters
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
except ImportError:
    print("❌ Error: scikit-learn not installed")
    print("   Run: pip install scikit-learn numpy")
    sys.exit(1)

from utils.formatters import print_section, print_box


class AcademicPerformanceML:
    """Machine Learning analyzer for academic performance"""
    
    def __init__(self, vtop_data: Dict):
        """Initialize with VTOP data"""
        self.data = vtop_data
        self.marks = vtop_data.get('marks', [])
        self.cgpa_trend = vtop_data.get('cgpa_trend', [])
        self.attendance = vtop_data.get('attendance', [])
    
    def cluster_courses(self, n_clusters=3) -> Dict:
        """
        Cluster courses based on performance metrics using KMeans
        
        Returns:
            Dictionary with cluster assignments and insights
        """
        if len(self.marks) < n_clusters:
            return {"error": "Not enough courses to cluster"}
        
        # Extract features for each course
        features = []
        course_names = []
        
        for course in self.marks:
            # Calculate current percentage
            total_scored = course.get('total_scored', 0)
            total_weight = course.get('total_weight', 40)
            percentage = (total_scored / total_weight * 100) if total_weight > 0 else 0
            
            # Get attendance
            attendance_pct = 0
            for att in self.attendance:
                if att.get('course_code') == course.get('course_code'):
                    attendance_pct = att.get('percentage', 0)
                    break
            
            # Calculate component consistency (variance in component scores)
            components = course.get('components', [])
            if components:
                component_scores = []
                for comp in components:
                    if comp.get('status') == 'Completed':
                        max_marks = comp.get('max_marks', 100)
                        scored = comp.get('scored_marks', 0)
                        comp_pct = (scored / max_marks * 100) if max_marks > 0 else 0
                        component_scores.append(comp_pct)
                
                consistency = np.std(component_scores) if len(component_scores) > 1 else 0
            else:
                consistency = 0
            
            features.append([percentage, attendance_pct, consistency])
            course_names.append(course.get('course_title', 'Unknown'))
        
        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features_normalized)
        
        # Calculate silhouette score (quality of clustering)
        silhouette = silhouette_score(features_normalized, cluster_labels)
        
        # Organize results
        clusters = {}
        for i in range(n_clusters):
            cluster_courses = []
            cluster_features = []
            
            for idx, label in enumerate(cluster_labels):
                if label == i:
                    cluster_courses.append(course_names[idx])
                    cluster_features.append(features[idx])
            
            # Calculate cluster center (mean of features)
            if cluster_features:
                center = np.mean(cluster_features, axis=0)
                clusters[f"Cluster {i+1}"] = {
                    "courses": cluster_courses,
                    "avg_percentage": round(center[0], 2),
                    "avg_attendance": round(center[1], 2),
                    "avg_consistency": round(center[2], 2),
                    "size": len(cluster_courses)
                }
        
        return {
            "clusters": clusters,
            "silhouette_score": round(silhouette, 3),
            "quality": "Excellent" if silhouette > 0.5 else "Good" if silhouette > 0.3 else "Fair"
        }
    
    def predict_final_grades(self) -> Dict:
        """
        Predict final grades using Linear Regression on completed components
        
        Returns:
            Dictionary with predictions for each course
        """
        predictions = {}
        
        for course in self.marks:
            course_code = course.get('course_code')
            course_title = course.get('course_title')
            components = course.get('components', [])
            
            if len(components) < 2:
                continue
            
            # Extract completed components
            completed = [c for c in components if c.get('status') == 'Completed']
            
            if len(completed) < 2:
                continue
            
            # Prepare data for regression
            X = []  # Component numbers
            y = []  # Scored percentages
            
            for idx, comp in enumerate(completed):
                max_marks = comp.get('max_marks', 100)
                scored = comp.get('scored_marks', 0)
                percentage = (scored / max_marks * 100) if max_marks > 0 else 0
                
                X.append([idx + 1])  # Component sequence
                y.append(percentage)
            
            # Fit regression model
            X_np = np.array(X)
            y_np = np.array(y)
            
            model = LinearRegression()
            model.fit(X_np, y_np)
            
            # Predict next component (assuming FAT is next)
            next_component_num = len(completed) + 1
            predicted_pct = model.predict([[next_component_num]])[0]
            
            # Ensure prediction is realistic (0-100)
            predicted_pct = max(0, min(100, predicted_pct))
            
            # Calculate trend (slope)
            slope = model.coef_[0]
            trend = "Improving" if slope > 2 else "Declining" if slope < -2 else "Stable"
            
            # Estimate final grade based on total projection
            total_scored = course.get('total_scored', 0)
            total_weight = course.get('total_weight', 40)
            remaining_weight = 100 - total_weight
            
            # Assume predicted percentage for remaining components
            projected_remaining = (predicted_pct / 100) * remaining_weight
            projected_total = total_scored + projected_remaining
            
            # Map to grade
            if projected_total >= 90:
                predicted_grade = 'S'
            elif projected_total >= 80:
                predicted_grade = 'A'
            elif projected_total >= 70:
                predicted_grade = 'B'
            elif projected_total >= 60:
                predicted_grade = 'C'
            elif projected_total >= 50:
                predicted_grade = 'D'
            else:
                predicted_grade = 'F'
            
            predictions[course_title] = {
                "current_total": round(total_scored, 2),
                "predicted_next_component": round(predicted_pct, 2),
                "trend": trend,
                "projected_total": round(projected_total, 2),
                "predicted_grade": predicted_grade,
                "confidence": "High" if len(completed) >= 3 else "Medium"
            }
        
        return predictions
    
    def analyze_cgpa_trajectory(self) -> Dict:
        """
        Analyze CGPA trend using regression to predict future CGPA
        
        Returns:
            Dictionary with CGPA trajectory analysis
        """
        if len(self.cgpa_trend) < 2:
            return {"error": "Insufficient CGPA history"}
        
        # Extract CGPA values
        semesters = []
        cgpa_values = []
        
        for idx, sem_data in enumerate(self.cgpa_trend):
            semesters.append(idx + 1)
            cgpa_values.append(sem_data.get('cgpa', 0))
        
        # Fit regression model
        X = np.array(semesters).reshape(-1, 1)
        y = np.array(cgpa_values)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next semester
        next_sem = len(semesters) + 1
        predicted_cgpa = model.predict([[next_sem]])[0]
        predicted_cgpa = max(0, min(10, predicted_cgpa))  # Clamp to 0-10
        
        # Calculate trend
        slope = model.coef_[0]
        r_squared = model.score(X, y)
        
        trend = "Improving" if slope > 0.05 else "Declining" if slope < -0.05 else "Stable"
        
        # Calculate volatility (standard deviation)
        volatility = np.std(cgpa_values)
        
        return {
            "current_cgpa": cgpa_values[-1],
            "predicted_next_cgpa": round(predicted_cgpa, 2),
            "trend": trend,
            "trend_strength": abs(round(slope, 3)),
            "r_squared": round(r_squared, 3),
            "volatility": round(volatility, 3),
            "consistency": "High" if volatility < 0.2 else "Medium" if volatility < 0.4 else "Low"
        }


def main():
    """Run ML analysis on VTOP data"""
    # Load data using the data manager
    from vtop_data_manager import get_vtop_data
    
    print("=" * 60)
    print("🤖 ACADEMIC PERFORMANCE ML ANALYZER")
    print("=" * 60)
    print()
    
    # Get data (will use cache if available)
    data = get_vtop_data(use_cache=True)
    
    # Initialize analyzer
    analyzer = AcademicPerformanceML(data)
    
    # 1. Course Clustering
    print_section("📊 COURSE CLUSTERING (KMeans Algorithm)")
    print("Grouping courses by performance similarity...\n")
    
    clustering = analyzer.cluster_courses()
    
    if "error" not in clustering:
        print(f"Clustering Quality: {clustering['quality']} (Silhouette Score: {clustering['silhouette_score']})\n")
        
        for cluster_name, cluster_data in clustering['clusters'].items():
            print(f"\n{cluster_name}:")
            print(f"  📈 Avg Performance: {cluster_data['avg_percentage']}%")
            print(f"  📅 Avg Attendance: {cluster_data['avg_attendance']}%")
            print(f"  📊 Consistency: {cluster_data['avg_consistency']:.2f}")
            print(f"  Courses ({cluster_data['size']}):")
            for course in cluster_data['courses']:
                print(f"    • {course}")
    else:
        print(f"⚠️  {clustering['error']}")
    
    print("\n" + "="*60 + "\n")
    
    # 2. Grade Prediction
    print_section("🎯 FINAL GRADE PREDICTION (Linear Regression)")
    print("Predicting final grades based on current performance...\n")
    
    predictions = analyzer.predict_final_grades()
    
    if predictions:
        for course, pred in predictions.items():
            print(f"\n📚 {course}")
            print(f"  Current: {pred['current_total']}/100")
            print(f"  Trend: {pred['trend']} ({pred['predicted_next_component']}% predicted for next component)")
            print(f"  Projected Total: {pred['projected_total']}/100")
            print(f"  Predicted Grade: {pred['predicted_grade']} (Confidence: {pred['confidence']})")
    else:
        print("⚠️  Not enough data for predictions")
    
    print("\n" + "="*60 + "\n")
    
    # 3. CGPA Trajectory
    print_section("📈 CGPA TRAJECTORY (Linear Regression)")
    print("Analyzing CGPA trend across semesters...\n")
    
    trajectory = analyzer.analyze_cgpa_trajectory()
    
    if "error" not in trajectory:
        print(f"Current CGPA: {trajectory['current_cgpa']}")
        print(f"Predicted Next Semester: {trajectory['predicted_next_cgpa']}")
        print(f"Trend: {trajectory['trend']} (Strength: {trajectory['trend_strength']})")
        print(f"Model Accuracy (R²): {trajectory['r_squared']}")
        print(f"Consistency: {trajectory['consistency']} (Volatility: {trajectory['volatility']})")
        
        if trajectory['trend'] == "Improving":
            print("\n✅ Your CGPA is on an upward trajectory! Keep up the good work!")
        elif trajectory['trend'] == "Declining":
            print("\n⚠️  Your CGPA shows a declining trend. Focus on improvement!")
        else:
            print("\n📊 Your CGPA is stable. Consider pushing for improvement!")
    else:
        print(f"⚠️  {trajectory['error']}")
    
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)


if __name__ == '__main__':
    main()
