'use client';

import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { Asset } from '../types/api';

export default function AssetList() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ asset_class: '', sector: '' });
  const [assetClasses, setAssetClasses] = useState<string[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);

  useEffect(() => {
    loadMetadata();
  }, []);

  useEffect(() => {
    loadAssets();
  }, [filter, loadAssets]);

  const loadMetadata = async () => {
    try {
      const [classesData, sectorsData] = await Promise.all([
        api.getAssetClasses(),
        api.getSectors()
      ]);
      setAssetClasses(classesData.asset_classes);
      setSectors(sectorsData.sectors);
    } catch (error) {
      console.error('Error loading metadata:', error);
    }
  };

  const loadAssets = useCallback(async () => {
    setLoading(true);
    try {
      const params: { asset_class?: string; sector?: string } = {};
      if (filter.asset_class) params.asset_class = filter.asset_class;
      if (filter.sector) params.sector = filter.sector;
      
      const data = await api.getAssets(params);
      setAssets(data);
    } catch (error) {
      console.error('Error loading assets:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Asset Class
            </label>
            <select
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              value={filter.asset_class}
              onChange={(e) => setFilter({ ...filter, asset_class: e.target.value })}
            >
              <option value="">All Classes</option>
              {assetClasses.map((ac) => (
                <option key={ac} value={ac}>{ac}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sector
            </label>
            <select
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              value={filter.sector}
              onChange={(e) => setFilter({ ...filter, sector: e.target.value })}
            >
              <option value="">All Sectors</option>
              {sectors.map((sector) => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Asset List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Class
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sector
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Market Cap
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : assets.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No assets found
                  </td>
                </tr>
              ) : (
                assets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {asset.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {asset.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {asset.asset_class}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {asset.sector}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {asset.currency} {asset.price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {asset.market_cap ? `$${(asset.market_cap / 1e9).toFixed(2)}B` : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
