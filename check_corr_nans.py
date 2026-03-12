from data.manager import DataManager
import math

def check_nans():
    dm = DataManager()
    data = dm.get_correlation_matrix()
    matrix = data.get('matrix', [])
    labels = data.get('labels', [])
    
    print(f"Labels: {labels}")
    nan_found = False
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val is None or math.isnan(val):
                print(f"NaN found at ({labels[i]}, {labels[j]})")
                nan_found = True
    
    if not nan_found:
        print("No NaNs found in the matrix.")

if __name__ == "__main__":
    check_nans()
