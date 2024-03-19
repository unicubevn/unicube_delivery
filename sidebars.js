/*
 * #  Copyright (c) by The UniCube, 2024.
 * #  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 * #  These code are maintained by The UniCube.
 */

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  unicubeSidebar: [{type: 'autogenerated', dirName: '.'}],

  // But you can create a sidebar manually
  /*
  unicubeSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['dashboard/create-a-document'],
    },
  ],
   */
};

export default sidebars;
