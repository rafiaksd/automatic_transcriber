from nemo.collections.asr.models import ClusteringDiarizer

from omegaconf import OmegaConf

cfg_dict = {
    "device": "cpu",
    "num_workers": 4,
    "sample_rate": 16000,
    "diarizer": {
        "manifest_filepath": "manifest.json",  # your manifest or audio list file path
        "out_dir": "diarization_output",
        "oracle_vad": False,
        "vad": {
            "model_path": "vad_multilingual_marblenet",
            "parameters": {
                "window_length_in_sec": 0.63,
                "shift_length_in_sec": 0.01,
                "smoothing": "median",
                "overlap": 0.5,
            },
        },
        "speaker_embeddings": {
            "model_path": "titanet_large",
            "parameters": {
                "window_length_in_sec": 1.5,
                "shift_length_in_sec": 0.75,
                "multiscale_weights": [1, 1, 1, 1],
            },
        },
        "clustering": {
            "parameters": {
                "oracle_num_speakers": False,
                "max_num_speakers": 10,
                "max_rp_threshold": 0.25,
            },
        },
    }
}



cfg = OmegaConf.create(cfg_dict)

diarizer = ClusteringDiarizer(cfg=cfg)

# Step 2: Set up the parameters
diarizer.diarize(paths2audio_files=["diarization_test.mp3"])