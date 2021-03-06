# Lint as: python3
# Copyright 2020, The TensorFlow Federated Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl.testing import absltest
from absl.testing import parameterized
import tensorflow as tf

from tensorflow_federated.python.core.api import computation_types
from tensorflow_federated.python.core.impl.types import placement_literals
from tensorflow_federated.python.core.impl.types import type_analysis


class CountTypesTest(parameterized.TestCase):

  # pyformat: disable
  @parameterized.named_parameters([
      ('one',
       computation_types.TensorType(tf.int32),
       computation_types.TensorType,
       1),
      ('three',
       computation_types.NamedTupleType([tf.int32] * 3),
       computation_types.TensorType,
       3),
      ('nested',
       computation_types.NamedTupleType([[tf.int32] * 3] * 3),
       computation_types.TensorType,
       9),
  ])
  # pyformat: enable
  def test_returns_result(self, type_signature, types, expected_result):
    result = type_analysis.count_types(type_signature, types)
    self.assertEqual(result, expected_result)


class ContainsTypesTest(parameterized.TestCase):

  # pyformat: disable
  @parameterized.named_parameters([
      ('one_type',
       computation_types.TensorType(tf.int32),
       computation_types.TensorType),
      ('two_types',
       computation_types.NamedTupleType([tf.int32]),
       (computation_types.NamedTupleType, computation_types.TensorType)),
      ('less_types',
       computation_types.TensorType(tf.int32),
       (computation_types.NamedTupleType, computation_types.TensorType)),
      ('more_types',
       computation_types.NamedTupleType([tf.int32]),
       computation_types.TensorType),
  ])
  # pyformat: enable
  def test_returns_true(self, type_signature, types):
    result = type_analysis.contains_types(type_signature, types)
    self.assertTrue(result)

  @parameterized.named_parameters([
      ('one_type', computation_types.TensorType(tf.int32),
       computation_types.NamedTupleType),
  ])
  def test_returns_false(self, type_signature, types):
    result = type_analysis.contains_types(type_signature, types)
    self.assertFalse(result)


class ContainsOnlyTypesTest(parameterized.TestCase):

  # pyformat: disable
  @parameterized.named_parameters([
      ('one_type',
       computation_types.TensorType(tf.int32),
       computation_types.TensorType),
      ('two_types',
       computation_types.NamedTupleType([tf.int32]),
       (computation_types.NamedTupleType, computation_types.TensorType)),
      ('less_types',
       computation_types.TensorType(tf.int32),
       (computation_types.NamedTupleType, computation_types.TensorType)),
  ])
  # pyformat: enable
  def test_returns_true(self, type_signature, types):
    result = type_analysis.contains_only_types(type_signature, types)
    self.assertTrue(result)

  # pyformat: disable
  @parameterized.named_parameters([
      ('one_type',
       computation_types.TensorType(tf.int32),
       computation_types.NamedTupleType),
      ('more_types',
       computation_types.NamedTupleType([tf.int32]),
       computation_types.TensorType),
  ])
  # pyformat: enable
  def test_returns_false(self, type_signature, types):
    result = type_analysis.contains_only_types(type_signature, types)
    self.assertFalse(result)


class CheckWellFormedTest(parameterized.TestCase):

  # pyformat: disable
  @parameterized.named_parameters([
      ('abstract_type',
       computation_types.AbstractType('T')),
      ('federated_type',
       computation_types.FederatedType(tf.int32, placement_literals.CLIENTS)),
      ('function_type',
       computation_types.FunctionType(tf.int32, tf.int32)),
      ('named_tuple_type',
       computation_types.NamedTupleType([tf.int32] * 3)),
      ('placement_type',
       computation_types.PlacementType()),
      ('sequence_type',
       computation_types.SequenceType(tf.int32)),
      ('tensor_type',
       computation_types.TensorType(tf.int32)),
  ])
  # pyformat: enable
  def test_does_not_raise_type_error(self, type_signature):
    try:
      type_analysis.check_well_formed(type_signature)
    except TypeError:
      self.fail('Raised TypeError unexpectedly.')

  @parameterized.named_parameters([
      ('federated_function_type',
       computation_types.FederatedType(
           computation_types.FunctionType(tf.int32, tf.int32),
           placement_literals.CLIENTS)),
      ('federated_federated_type',
       computation_types.FederatedType(
           computation_types.FederatedType(tf.int32,
                                           placement_literals.CLIENTS),
           placement_literals.CLIENTS)),
      ('sequence_sequence_type',
       computation_types.SequenceType(
           computation_types.SequenceType([tf.int32]))),
      ('sequence_federated_type',
       computation_types.SequenceType(
           computation_types.FederatedType(tf.int32,
                                           placement_literals.CLIENTS))),
      ('tuple_federated_function_type',
       computation_types.NamedTupleType([
           computation_types.FederatedType(
               computation_types.FunctionType(tf.int32, tf.int32),
               placement_literals.CLIENTS)
       ])),
      ('tuple_federated_federated_type',
       computation_types.NamedTupleType([
           computation_types.FederatedType(
               computation_types.FederatedType(tf.int32,
                                               placement_literals.CLIENTS),
               placement_literals.CLIENTS)
       ])),
      ('federated_tuple_function_type',
       computation_types.FederatedType(
           computation_types.NamedTupleType(
               [computation_types.FunctionType(tf.int32, tf.int32)]),
           placement_literals.CLIENTS)),
  ])
  # pyformat: enable
  def test_raises_type_error(self, type_signature):
    with self.assertRaises(TypeError):
      type_analysis.check_well_formed(type_signature)


if __name__ == '__main__':
  absltest.main()
