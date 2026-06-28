(function () {
    function getGoldenLayoutConstructor() {
        if (window.goldenLayout && window.goldenLayout.GoldenLayout) {
            return window.goldenLayout.GoldenLayout;
        }
        if (window.GoldenLayout) {
            return window.GoldenLayout;
        }
        return null;
    }

    function derivePanelTitle(element, index) {
        const explicitTitle = element.getAttribute('data-gl-title');
        if (explicitTitle) {
            return explicitTitle;
        }

        const heading = element.querySelector('h1, h2, h3, h4, h5, .card-title');
        if (heading && heading.textContent.trim()) {
            return heading.textContent.trim().slice(0, 60);
        }

        return `Panel ${index + 1}`;
    }

    function selectPanelCandidates(main) {
        const explicitPanels = Array.from(main.querySelectorAll('[data-gl-panel="true"]'));
        if (explicitPanels.length > 0) {
            return explicitPanels;
        }

        const topLevel = Array.from(main.children).filter((element) => element.tagName !== 'SCRIPT');
        if (topLevel.length > 1) {
            return topLevel;
        }

        if (topLevel.length === 1) {
            const child = topLevel[0];
            const nestedSections = Array.from(child.children).filter((element) => {
                if (element.tagName === 'SCRIPT') {
                    return false;
                }
                return element.matches('section, article, aside, .card, .row, [class*="col-"]');
            });

            if (nestedSections.length > 1) {
                return nestedSections;
            }
        }

        return topLevel;
    }

    function createSources() {
        const fallbackRoot = document.getElementById('app-fallback-root');
        const navSource = document.getElementById('gl-nav-source');
        const sourceRoot = document.getElementById('gl-source-panels');

        if (!fallbackRoot || !navSource || !sourceRoot) {
            return null;
        }

        const nav = fallbackRoot.querySelector('nav');
        const main = fallbackRoot.querySelector('main');
        const flashContainer = fallbackRoot.querySelector('.container.mt-3');
        const panels = [];

        if (nav) {
            navSource.appendChild(nav);
        }

        if (main && flashContainer) {
            main.prepend(flashContainer);
        }

        if (!main) {
            return { panels };
        }

        const panelCandidates = selectPanelCandidates(main);
        panelCandidates.forEach((element, index) => {
            const wrapper = document.createElement('div');
            const panelId = `gl-generated-panel-${index}`;
            wrapper.id = panelId;
            wrapper.className = 'gl-source-panel gl-content-panel';
            wrapper.appendChild(element);
            sourceRoot.appendChild(wrapper);
            panels.push({
                sourceId: panelId,
                title: derivePanelTitle(element, index),
            });
        });

        return { panels };
    }

    function bootstrapDropdowns(rootElement) {
        const toggles = rootElement.querySelectorAll('[data-bs-toggle="dropdown"]');
        toggles.forEach((toggle) => {
            if (window.bootstrap && window.bootstrap.Dropdown) {
                new window.bootstrap.Dropdown(toggle);
            }
        });
    }

    function buildPanelConfig(panels) {
        if (panels.length === 0) {
            return {
                type: 'component',
                componentName: 'panel',
                title: 'Workspace',
                componentState: { sourceId: 'gl-main-source' },
                isClosable: false
            };
        }

        if (panels.length === 1) {
            return {
                type: 'component',
                componentName: 'panel',
                title: panels[0].title,
                componentState: { sourceId: panels[0].sourceId },
                isClosable: false
            };
        }

        if (panels.length === 2) {
            return {
                type: 'row',
                content: panels.map((panel) => ({
                    type: 'component',
                    componentName: 'panel',
                    title: panel.title,
                    componentState: { sourceId: panel.sourceId },
                    isClosable: false
                }))
            };
        }

        return {
            type: 'column',
            content: [
                {
                    type: 'row',
                    height: 58,
                    content: panels.slice(0, 2).map((panel) => ({
                        type: 'component',
                        componentName: 'panel',
                        title: panel.title,
                        componentState: { sourceId: panel.sourceId },
                        isClosable: false
                    }))
                },
                {
                    type: 'stack',
                    height: 42,
                    content: panels.slice(2).map((panel) => ({
                        type: 'component',
                        componentName: 'panel',
                        title: panel.title,
                        componentState: { sourceId: panel.sourceId },
                        isClosable: false
                    }))
                }
            ]
        };
    }

    function initGoldenLayout() {
        const GoldenLayoutCtor = getGoldenLayoutConstructor();
        const root = document.getElementById('golden-layout-root');
        if (!GoldenLayoutCtor || !root) {
            return;
        }

        const sourceResult = createSources();
        if (!sourceResult) {
            return;
        }

        try {
            const config = {
                settings: {
                    hasHeaders: true,
                    constrainDragToContainer: true,
                    reorderEnabled: true,
                    selectionEnabled: false,
                    popoutWholeStack: false,
                    blockedPopoutsThrowError: false,
                    closePopoutsOnUnload: true,
                    showPopoutIcon: false,
                    showMaximiseIcon: true,
                    showCloseIcon: false
                },
                dimensions: {
                    borderWidth: 5,
                    minItemHeight: 60,
                    minItemWidth: 120,
                    headerHeight: 30,
                    dragProxyWidth: 320,
                    dragProxyHeight: 240
                },
                content: [
                    {
                        type: 'row',
                        content: [
                            {
                                type: 'component',
                                componentName: 'panel',
                                title: 'Navigation',
                                width: 22,
                                isClosable: false,
                                componentState: {
                                    sourceId: 'gl-nav-source',
                                    bootstrapDropdowns: true
                                }
                            },
                            {
                                type: 'stack',
                                width: 78,
                                isClosable: false,
                                content: [
                                    buildPanelConfig(sourceResult.panels)
                                ]
                            }
                        ]
                    }
                ]
            };

            const layout = new GoldenLayoutCtor(config, root);
            layout.registerComponent('panel', function (container, state) {
                const source = document.getElementById(state.sourceId);
                if (!source) {
                    return;
                }

                const element = container.getElement ? container.getElement() : container.element;
                const target = element.jquery ? element[0] : element;
                target.appendChild(source);

                if (state.bootstrapDropdowns) {
                    bootstrapDropdowns(target);
                }
            });

            layout.init();
            document.body.classList.add('gl-enabled');

            window.addEventListener('resize', () => {
                if (typeof layout.updateSize === 'function') {
                    layout.updateSize();
                }
            });
        } catch (error) {
            console.error('Golden Layout init failed:', error);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGoldenLayout);
    } else {
        initGoldenLayout();
    }
})();
