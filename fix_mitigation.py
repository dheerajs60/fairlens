import re

def fix_mitigation(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Add Union, Dict import
    if 'from typing import' not in content:
        content = 'from typing import Union, Dict\n' + content
    else:
        content = re.sub(r'(from typing import .*?)\n', r'\1, Union, Dict\n', content, count=1)

    # Change signature
    content = content.replace(
        'def run_mitigation(audit_id: str, reweighing_strength: float, threshold_adjust: float, apply_post: bool) -> MitigationResponse:',
        'def run_mitigation(audit_id: str, reweighing_strength: Union[float, Dict[str, float]], threshold_adjust: float, apply_post: bool) -> MitigationResponse:'
    )

    # Replace the apply_post logic
    old_apply_post = """    # If AUTO-CORRECT is on, force maximum strengths
    if apply_post:
        reweighing_strength = 1.0
        threshold_adjust = 1.0"""
    
    new_apply_post = """    # If AUTO-CORRECT is on, force maximum strengths
    if apply_post:
        if isinstance(reweighing_strength, dict):
            reweighing_strength = {k: 1.0 for k in sensitive_attrs}
        else:
            reweighing_strength = 1.0
        threshold_adjust = 1.0"""
    
    content = content.replace(old_apply_post, new_apply_post)

    # Replace the reweighing logic
    old_reweighing = """    # PHASE A: IN-PROCESSING (REWEIGHING)
    # If strength > 0, we re-train with sample weights to balance outcomes
    if reweighing_strength > 0.1:
        # Calculate sample weights for Demographic Parity
        y_total = len(y_train)
        y_pos = y_train.sum()
        y_neg = y_total - y_pos
        
        weights = pd.Series(1.0, index=y_train.index)
        for group in sa_train.unique():
            mask = (sa_train == group)
            group_total = mask.sum()
            if group_total == 0: continue
            
            group_pos = (y_train[mask] == 1).sum()
            group_neg = group_total - group_pos
            
            # Theoretical weights to achieve parity
            # If group has fewer positives than average, boost its positives
            target_pos_rate = y_pos / y_total
            current_pos_rate = group_pos / group_total
            
            if group_pos > 0:
                pos_weight = target_pos_rate / current_pos_rate
                weights[mask & (y_train == 1)] = 1.0 + (pos_weight - 1.0) * reweighing_strength
            
            # If group has more negatives than average, boost its negatives
            target_neg_rate = y_neg / y_total
            current_neg_rate = group_neg / group_total
            
            if group_neg > 0:
                neg_weight = target_neg_rate / current_neg_rate
                weights[mask & (y_train == 0)] = 1.0 + (neg_weight - 1.0) * reweighing_strength
        
        # Ensure weights are positive and not too crazy
        weights = weights.clip(lower=0.1, upper=10.0)
        
        # Re-train Random Forest with weights
        new_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        new_model.fit(X_train, y_train, sample_weight=weights)
        current_model = new_model
        final_preds = current_model.predict(X_test)"""

    new_reweighing = """    # PHASE A: IN-PROCESSING (REWEIGHING)
    # If strength > 0, we re-train with sample weights to balance outcomes
    has_reweighing = False
    if isinstance(reweighing_strength, dict):
        has_reweighing = any(v > 0.1 for v in reweighing_strength.values())
    else:
        has_reweighing = reweighing_strength > 0.1

    if has_reweighing:
        # Calculate sample weights for Demographic Parity
        y_total = len(y_train)
        y_pos = y_train.sum()
        y_neg = y_total - y_pos
        
        weights = pd.Series(1.0, index=y_train.index)
        
        for attr in sensitive_attrs:
            sa_train_attr = sensitive_train[attr]
            attr_strength = reweighing_strength.get(attr, 0.5) if isinstance(reweighing_strength, dict) else reweighing_strength
            
            if attr_strength <= 0.1:
                continue
                
            attr_weights = pd.Series(1.0, index=y_train.index)
            for group in sa_train_attr.unique():
                mask = (sa_train_attr == group)
                group_total = mask.sum()
                if group_total == 0: continue
                
                group_pos = (y_train[mask] == 1).sum()
                group_neg = group_total - group_pos
                
                # Theoretical weights to achieve parity
                target_pos_rate = y_pos / y_total
                current_pos_rate = group_pos / group_total
                if group_pos > 0:
                    pos_weight = target_pos_rate / current_pos_rate
                    attr_weights[mask & (y_train == 1)] = 1.0 + (pos_weight - 1.0) * attr_strength
                
                target_neg_rate = y_neg / y_total
                current_neg_rate = group_neg / group_total
                if group_neg > 0:
                    neg_weight = target_neg_rate / current_neg_rate
                    attr_weights[mask & (y_train == 0)] = 1.0 + (neg_weight - 1.0) * attr_strength
            
            # Multiply intersectional weights
            weights *= attr_weights
        
        # Ensure weights are positive and not too crazy
        weights = weights.clip(lower=0.1, upper=10.0)
        
        # Re-train Random Forest with weights
        new_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        new_model.fit(X_train, y_train, sample_weight=weights)
        current_model = new_model
        final_preds = current_model.predict(X_test)"""
        
    content = content.replace(old_reweighing, new_reweighing)
    
    with open(file_path, 'w') as f:
        f.write(content)

fix_mitigation("/Users/kovoordheeraj/Documents/google solutions updated/fairlens-main/backend/services/mitigation_service.py")
fix_mitigation("/Users/kovoordheeraj/Documents/google solutions updated/google_solutions-main/backend/services/mitigation_service.py")
print("Done")
