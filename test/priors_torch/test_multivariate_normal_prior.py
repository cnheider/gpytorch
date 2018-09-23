from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import torch
from gpytorch.priors_torch import MultivariateNormalPrior
from torch.distributions import MultivariateNormal


class TestMultivariateNormalPrior(unittest.TestCase):
    def test_multivariate_normal_prior_to_gpu(self):
        if torch.cuda.is_available():
            prior = MultivariateNormalPrior(
                torch.tensor([0.0, 1.0]), covariance_matrix=torch.eye(2)
            ).cuda()
            self.assertEqual(prior.loc.device.type, "cuda")
            self.assertEqual(prior.covariance_matrix.device.type, "cuda")
            self.assertEqual(prior.scale_tril.device.type, "cuda")
            self.assertEqual(prior.precision_matrix.device.type, "cuda")

    def test_multivariate_normal_prior_validate_args(self):
        # This should be a ValueError in pytorch, see pytorch Github issue #11997
        with self.assertRaises(RuntimeError):
            mean = torch.tensor([0.0, 1.0])
            cov = torch.tensor([[1.0, 2.0], [2.0, 0.5]])
            MultivariateNormalPrior(mean, covariance_matrix=cov, validate_args=True)

    def test_multivariate_normal_prior_log_prob(self, cuda=False):
        device = torch.device("cuda") if cuda else torch.device("cpu")
        mean = torch.tensor([0.0, 1.0], device=device)
        cov = torch.eye(2, device=device)
        prior = MultivariateNormalPrior(mean, covariance_matrix=cov)
        dist = MultivariateNormal(mean, covariance_matrix=cov)

        self.assertFalse(prior.log_transform)
        t = torch.tensor([-1, 0.5], device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        t = torch.tensor([[-1, 0.5], [1.5, -2.0]], device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        with self.assertRaises(RuntimeError):
            prior.log_prob(torch.zeros(3, device=device))

    def test_multivariate_normal_prior_log_prob_cuda(self):
        if torch.cuda.is_available():
            return self.test_multivariate_normal_prior_log_prob(cuda=True)

    def test_multivariate_normal_prior_log_prob_log_transform(self, cuda=False):
        device = torch.device("cuda") if cuda else torch.device("cpu")
        mean = torch.tensor([0.0, 1.0], device=device)
        cov = torch.eye(2, device=device)
        prior = MultivariateNormalPrior(mean, covariance_matrix=cov, log_transform=True)
        dist = MultivariateNormal(mean, covariance_matrix=cov)

        self.assertTrue(prior.log_transform)
        t = torch.tensor([-1, 0.5], device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t.exp())))
        t = torch.tensor([[-1, 0.5], [1.5, -2.0]], device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t.exp())))
        with self.assertRaises(RuntimeError):
            prior.log_prob(torch.zeros(3, device=device))

    def test_multivariate_normal_prior_log_prob_log_transform_cuda(self):
        if torch.cuda.is_available():
            return self.test_multivariate_normal_prior_log_prob(cuda=True)

    def test_multivariate_normal_prior_batch_log_prob(self, cuda=False):
        device = torch.device("cuda") if cuda else torch.device("cpu")

        mean = torch.tensor([[0.0, 1.0], [-0.5, 2.0]], device=device)
        cov = torch.eye(2, device=device).repeat(2, 1, 1)
        prior = MultivariateNormalPrior(mean, covariance_matrix=cov)
        dist = MultivariateNormal(mean, covariance_matrix=cov)

        self.assertFalse(prior.log_transform)
        t = torch.tensor([-1, 0.5], device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        t = torch.tensor([[-1, 0.5], [1.5, -2.0]], device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        with self.assertRaises(RuntimeError):
            prior.log_prob(torch.zeros(1, 3, device=device))

        mean = torch.rand(3, 2, 2, device=device)
        cov = torch.eye(2, device=device).repeat(3, 2, 1, 1)
        prior = MultivariateNormalPrior(mean, covariance_matrix=cov)
        dist = MultivariateNormal(mean, covariance_matrix=cov)

        t = torch.rand(2, device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        t = torch.rand(2, 2, device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        t = torch.rand(3, 2, 2, device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        t = torch.rand(2, 3, 2, 2, device=device)
        self.assertTrue(torch.equal(prior.log_prob(t), dist.log_prob(t)))
        with self.assertRaises(RuntimeError):
            prior.log_prob(torch.rand(3, device=device))
        with self.assertRaises(RuntimeError):
            prior.log_prob(torch.rand(3, 2, 3, device=device))

    def test_multivariate_normal_prior_batch_log_prob_cuda(self):
        if torch.cuda.is_available():
            return self.test_multivariate_normal_prior_batch_log_prob(cuda=True)


if __name__ == "__main__":
    unittest.main()
