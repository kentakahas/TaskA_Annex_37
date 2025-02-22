"""Continue training on existing model."""

import os
import json
from models import TFT_Predictor


def main(
        model_group_name, model_architecture, predictor_model,
        model_type, model_name, building_index,
        train_path, val_path
    ):

    # load model group - note ordering does not matter
    model_group = predictor_model(model_group_name, load='group')

    # check requested model is valid
    if model_type in ['load','solar']:
        assert model_name in model_group.model_names[model_type], f"{model_name} is not a valid {model_type} model in model group '{model_group_name}'."
    elif model_type in ['pricing','carbon']:
        assert model_name == model_group.model_names[model_type], f"{model_name} is not a valid {model_type} model in model group '{model_group_name}'."
    else:
        raise ValueError("`model_type` argument must be one of ('load','solar','pricing','carbon').")

    # construct train & validate datasets
    train_ds,val_ds = model_group.format_CityLearn_datasets([train_path,val_path], model_type=model_type, model_name=model_name, building_index=building_index)

    # continue training on specified model
    model_group.train_model(model_name,model_type,train_ds,val_ds)


if __name__ == '__main__':

    # set paths for train & validation datasets for training
    dataset_path = os.path.join('data','example')
    train_path = os.path.join(dataset_path,'train')
    val_path = os.path.join(dataset_path,'validate')

    # grab building ids in specified dataset
    with open(os.path.join(train_path,'metadata_ext.json')) as json_file:
        UCam_ids = json.load(json_file)["UCam_building_ids"]

    # specify model to be trained
    model_group_name = 'test'
    model_architecture = 'TFT'
    predictor_model = TFT_Predictor

    model_type = 'load'
    model_name = f'load_{UCam_ids[0]}'
    building_index = 0

    main(
        model_group_name, model_architecture, predictor_model,
        model_type, model_name, building_index,
        train_path, val_path
    )