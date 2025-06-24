import { shallowMount } from '@vue/test-utils'
import StatusDisplay from '../StatusDisplay.vue'

describe('StatusDisplay', () => {
  it('renders status text passed as prop', () => {
    const status = 'Processing...';
    const wrapper = shallowMount(StatusDisplay, {
      propsData: { status }
    });
    expect(wrapper.text()).toContain(status);
  });
}); 