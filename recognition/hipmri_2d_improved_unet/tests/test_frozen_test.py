"""Constructed CPU-only checks; no real test data or model evaluation is used."""

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import torch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import evaluate_frozen_test as frozen
from audit_test_manifest import pair_metadata
from dataset import preprocess_pair
from train import manifest_hash


TEMP_ROOT = PROJECT.parents[1] / "outputs/test_tmp"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


class TinyFrozenModel(torch.nn.Module):
    """Six scripted class logits, not a trained MRI segmentation model."""

    def __init__(self, mutate=False):
        super().__init__()
        self.bias = torch.nn.Parameter(torch.tensor([0., 0., 0., 0., 0., 3.]))
        self.mutate = mutate

    def forward(self, image):
        if self.mutate:
            self.bias.add_(1)
        return self.bias.reshape(1, 6, 1, 1).expand(image.shape[0], 6, *image.shape[-2:])


def fixture(root, overlap=False):
    project = root / "project"
    project.mkdir()
    for name in frozen.REQUIRED_SOURCES:
        (project / name).write_bytes(b"constructed source only")
    data = root / "constructed_data"
    all_pairs = {}
    summaries = {}
    for split, case, count in (("training", 3 if overlap else 1, 1), ("validation", 2, 1), ("test", 3, 5)):
        images, masks = (data / name for name in frozen.SPLIT_FOLDERS[split])
        images.mkdir(parents=True)
        masks.mkdir(parents=True)
        pairs = []
        for index in range(count):
            image = images / f"case_{case:03d}_week_0_slice_{index}.nii.gz"
            mask = masks / f"seg_{case:03d}_week_0_slice_{index}.nii.gz"
            image.write_bytes(f"constructed image bytes {index}".encode())
            mask.write_bytes(f"constructed mask bytes {index}".encode())
            pairs.append((image, mask))
        all_pairs[split] = pairs
        summaries[split] = {"pairs": count, "manifest_sha256": manifest_hash(pairs),
                            "case_proxy_ids": [case], "image_folder": images.name, "mask_folder": masks.name}
    audit = {"status": "passed_full", "splits": deepcopy(summaries), "test_files": []}
    for (image, mask), metadata in zip(all_pairs["test"], pair_metadata(all_pairs["test"])):
        audit["test_files"].append({**metadata, "status": "passed", "image_sha256": frozen.sha(image),
                                    "mask_sha256": frozen.sha(mask), "image_bytes": image.stat().st_size,
                                    "mask_bytes": mask.stat().st_size})
    content = "\n".join(f"{r['image']}|{r['mask']}|{r['image_sha256']}|{r['mask_sha256']}" for r in audit["test_files"])
    audit["test_content_manifest_sha256"] = hashlib.sha256(content.encode()).hexdigest()
    audit_path = root / "audit.json"
    models = []
    for name, epoch in frozen.MODEL_EPOCHS:
        original = root / f"{name}_original.pt"
        snapshot = root / f"{name}_frozen.pt"
        config = {"in_channels": 1, "num_classes": 6, "base_channels": 16}
        saved = {"model": name, "model_config": config, "epoch": epoch, "seed": 3710,
                 "validation_cross_entropy": .1, "validation_id5_dice": .8,
                 "limited_training_smoke": False, "selection_metric": "id5_dice",
                 "model_state": TinyFrozenModel().state_dict()}
        torch.save(saved, original)
        shutil.copyfile(original, snapshot)
        models.append({"model": name, "epoch": epoch, "model_config": config, "parameters": 6,
                       "validation_cross_entropy": .1, "validation_id5_dice": .8,
                       "checkpoint": snapshot.name, "original_checkpoint": original.name,
                       "checkpoint_sha256": frozen.sha(snapshot)})
    evaluation = {"seed": 3710, "batch_size": 4, "num_workers": 0, "precision": "FP32", "device": "cpu",
                  "shuffle": False, "drop_last": False, "aggregation": "pixel_pooled", "prediction": "argmax",
                  "num_classes": 6, "test_time_augmentation": False, "threshold_tuning": False,
                  "one_pass_per_model": True, "post_test_tuning": False}
    source = {name: frozen.sha(project / name) for name in frozen.REQUIRED_SOURCES}
    old = root / "old_result.json"
    old.write_bytes(b"original record")
    recipe = {"frozen_before_test_manifest_or_pixel_read": True, "user_confirmation_received": True,
              "models": deepcopy(models), "evaluation": deepcopy(evaluation), "source_sha256": deepcopy(source),
              "protected_original_files_sha256": {old.name: frozen.sha(old)},
              "prior_id5_plan_sha256": "f" * 64}
    recipe_path = root / "recipe.json"
    write(recipe_path, recipe)
    audit.update(frozen_plan_sha256=frozen.sha(recipe_path), prior_plan_sha256=recipe["prior_id5_plan_sha256"],
                 source_sha256={name: source[name] for name in ("dataset.py", "train.py", "audit_test_manifest.py")})
    write(audit_path, audit)
    summaries["test"]["test_content_manifest_sha256"] = audit["test_content_manifest_sha256"]
    summaries["test"]["valid_pixels"] = 4 * 256 + 272
    plan = {"status": "approved_for_execution", "user_confirmation_received": True,
            "synthetic_test_only": True, "source_revision": "constructed-only", "once_guard": frozen.ONCE_GUARD,
            "models": models, "evaluation": evaluation, "source_sha256": source,
            "protected_original_files_sha256": {old.name: frozen.sha(old)},
            "recipe_file": recipe_path.name, "recipe_sha256": frozen.sha(recipe_path),
            "audit_file": audit_path.name, "audit_sha256": frozen.sha(audit_path), "data": summaries}
    plan_path = root / "plan.json"
    write(plan_path, plan)
    samples = [preprocess_pair(torch.arange(256, dtype=torch.float32).reshape(1, 16, 16),
                               torch.full((16, 16), 5 if index < 2 else 0, dtype=torch.long)) for index in range(4)]
    samples.append(preprocess_pair(torch.arange(272, dtype=torch.float32).reshape(1, 16, 17),
                                   torch.full((16, 17), 5, dtype=torch.long)))
    args = argparse.Namespace(plan=plan_path, data_root=data, output_dir=root / "new_output", device="cpu")
    return {"project": project, "args": args, "samples": samples, "plan": plan, "pairs": all_pairs,
            "plan_path": plan_path, "old": old}


class FrozenTestChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        previous = torch.get_num_threads()
        self.addCleanup(torch.set_num_threads, previous)

    def run_constructed(self, root, value, model_factory=None):
        with patch("evaluate_frozen_test.HipMRIPairDataset", return_value=value["samples"]), \
                patch("evaluate_frozen_test.build_model", side_effect=model_factory or (lambda *a, **k: TinyFrozenModel())), \
                patch("evaluate_frozen_test.torch.cuda.is_available", return_value=False):
            return frozen.execute(value["args"], root=root, project=value["project"], allow_cpu_for_synthetic=True)

    def test_one_pass_tail_batch_shared_metrics_and_persistent_guard(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            report = self.run_constructed(root, value)
            self.assertEqual(report["status"], "passed")
            self.assertEqual(frozen.read(root / frozen.ONCE_GUARD)["status"], "passed")
            for name, _ in frozen.MODEL_EPOCHS:
                entry = report["models"][name]
                self.assertEqual((entry["forward_calls"], entry["forward_samples"]), (2, 5))
                self.assertEqual((entry["metrics"]["samples"], entry["metrics"]["batches"], entry["optimizer_steps"]), (5, 2, 0))
                self.assertEqual(entry["metrics"]["valid_pixels"], 1296)
                self.assertEqual(entry["metrics"]["confusion_matrix"][5][5], 784)
                self.assertEqual(entry["metrics"]["confusion_matrix"][0][5], 512)
                self.assertAlmostEqual(entry["metrics"]["dice_per_class"][5], 1568 / 2080)
                expected_ce = math.log(5 + math.exp(3)) - 3 * 784 / 1296
                self.assertAlmostEqual(entry["metrics"]["cross_entropy"], expected_ce, places=6)
                self.assertEqual(entry["state_sha256_before"], entry["state_sha256_after"])
                self.assertTrue(entry["parameters_have_no_gradients"])
                self.assertEqual(frozen.read(value["args"].output_dir / f"{name}_result.json"), entry)
            self.assertEqual(report["content_verification_before"], report["content_verification_after"])

    def test_changed_output_or_plan_cannot_repeat_a_completed_attempt(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            self.run_constructed(root, value)
            value["args"].output_dir = root / "another_output"
            value["plan"]["extra_note"] = "a different plan must not bypass once"
            second = root / "second_plan.json"
            write(second, value["plan"])
            value["args"].plan = second
            with self.assertRaisesRegex(ValueError, "attempt already exists"):
                self.run_constructed(root, value)
            self.assertFalse(value["args"].output_dir.exists())

    def test_second_model_failure_preserves_first_model_result_and_consumes_attempt(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            def build(name, **kwargs):
                if name == "improved_unet":
                    raise RuntimeError("constructed second-model failure")
                return TinyFrozenModel()
            with self.assertRaisesRegex(RuntimeError, "constructed second-model"):
                self.run_constructed(root, value, build)
            report = frozen.read(root / frozen.ONCE_GUARD)
            self.assertEqual(report["status"], "incomplete")
            self.assertEqual(report["models"]["baseline_unet"]["status"], "passed")
            self.assertEqual(report["models"]["improved_unet"]["status"], "incomplete")
            self.assertEqual(frozen.read(value["args"].output_dir / "baseline_unet_result.json")["full_test_passes"], 1)
            value["args"].output_dir = root / "retry_output"
            with self.assertRaisesRegex(ValueError, "attempt already exists"):
                self.run_constructed(root, value)

    def test_model_state_mutation_is_detected_without_rerunning(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            with self.assertRaisesRegex(ValueError, "change model state"):
                self.run_constructed(root, value, lambda *a, **k: TinyFrozenModel(mutate=True))
            report = frozen.read(root / frozen.ONCE_GUARD)
            self.assertEqual(report["status"], "incomplete")
            self.assertEqual(report["models"]["baseline_unet"]["forward_calls"], 2)
            self.assertNotIn("improved_unet", report["models"])

    def test_source_drift_stops_before_once_claim_or_forward(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            (value["project"] / "dataset.py").write_bytes(b"changed preprocessing")
            with self.assertRaisesRegex(ValueError, "source changed"):
                self.run_constructed(root, value)
            self.assertFalse((root / frozen.ONCE_GUARD).exists())

    def test_test_compressed_bytes_drift_stops_before_any_forward(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            value["pairs"]["test"][0][0].write_bytes(b"changed bytes")
            with self.assertRaisesRegex(ValueError, "compressed file bytes changed"):
                self.run_constructed(root, value)
            self.assertFalse((root / frozen.ONCE_GUARD).exists())

    def test_case_group_leakage_stops_before_any_forward(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root, overlap=True)
            with self.assertRaisesRegex(ValueError, "Case groups overlap"):
                self.run_constructed(root, value)
            self.assertFalse((root / frozen.ONCE_GUARD).exists())

    def test_audit_must_bind_to_the_same_recipe_and_prior_plan(self):
        for field, message in (("frozen_plan_sha256", "different frozen recipe"),
                               ("prior_plan_sha256", "different prior ID5 plan")):
            with self.subTest(field=field), tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
                root = Path(folder)
                value = fixture(root)
                audit_path = root / value["plan"]["audit_file"]
                audit = frozen.read(audit_path)
                audit[field] = "0" * 64
                write(audit_path, audit)
                # Even a caller updating the audit-file SHA cannot change its binding.
                value["plan"]["audit_sha256"] = frozen.sha(audit_path)
                write(value["plan_path"], value["plan"])
                with self.assertRaisesRegex(ValueError, message):
                    self.run_constructed(root, value)
                self.assertFalse((root / frozen.ONCE_GUARD).exists())

    def test_recipe_protected_inventory_and_audit_sources_cannot_be_dropped(self):
        for change in ("protected_omission", "audit_source"):
            with self.subTest(change=change), tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
                root = Path(folder)
                value = fixture(root)
                if change == "protected_omission":
                    another = root / "another_result.json"
                    another.write_bytes(b"another protected record")
                    value["plan"]["protected_original_files_sha256"] = {another.name: frozen.sha(another)}
                    message = "Protected original records differ"
                else:
                    audit_path = root / value["plan"]["audit_file"]
                    audit = frozen.read(audit_path)
                    audit["source_sha256"]["dataset.py"] = "0" * 64
                    write(audit_path, audit)
                    value["plan"]["audit_sha256"] = frozen.sha(audit_path)
                    message = "Audit source hashes differ"
                write(value["plan_path"], value["plan"])
                with self.assertRaisesRegex(ValueError, message):
                    self.run_constructed(root, value)
                self.assertFalse((root / frozen.ONCE_GUARD).exists())

    def test_changed_recipe_controls_or_guard_path_are_rejected(self):
        for field, value_to_set in (("prediction", "threshold"), ("post_test_tuning", True)):
            with self.subTest(field=field), tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
                root = Path(folder)
                value = fixture(root)
                value["plan"]["evaluation"][field] = value_to_set
                write(value["plan_path"], value["plan"])
                with self.assertRaisesRegex(ValueError, "Evaluation controls differ"):
                    self.run_constructed(root, value)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            value["plan"]["once_guard"] = "outputs/another.guard.json"
            write(value["plan_path"], value["plan"])
            with self.assertRaisesRegex(ValueError, "fixed once guard"):
                self.run_constructed(root, value)

    def test_checkpoint_epoch_and_frozen_copy_bytes_are_verified(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            value = fixture(root)
            wrong_epoch = dict(value["plan"]["models"][0], epoch=6)
            with self.assertRaisesRegex(ValueError, "checkpoint epoch differs"):
                frozen.verify_checkpoint(wrong_epoch, root)
            frozen_path = root / value["plan"]["models"][0]["checkpoint"]
            frozen_path.write_bytes(b"not the frozen checkpoint")
            with self.assertRaisesRegex(ValueError, "checkpoint bytes changed"):
                frozen.verify_checkpoint(value["plan"]["models"][0], root)

    def test_once_claim_is_exclusive_and_does_not_delete_failed_attempt(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as folder:
            root = Path(folder)
            frozen.claim_once(root, {"status": "incomplete", "plan_sha256": "a" * 64})
            with self.assertRaises(FileExistsError):
                frozen.claim_once(root, {"status": "running", "plan_sha256": "b" * 64})
            self.assertEqual(frozen.read(root / frozen.ONCE_GUARD)["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
